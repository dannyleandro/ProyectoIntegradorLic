import os
import psycopg2
import boto3
from psycopg2.extras import RealDictCursor
from datetime import datetime
from botocore.exceptions import ClientError
from apscheduler.schedulers.blocking import BlockingScheduler


def crear_notificaciones():
    print('Inicia')
    try:
        connection = psycopg2.connect(host=os.environ['HOSTDB'], port=os.environ['PORTDB'],
                                      database=os.environ['NAMEDB'], user=os.environ['USERDB'],
                                      password=os.environ['PASSDB'])
        cur = connection.cursor(cursor_factory=RealDictCursor)
        query_codes = """
                    SELECT "IdProcess", "ClassCode" FROM public.negociospush_process
                    WHERE "SystemLoadDate" > now() - INTERVAL '1 day'
                    """
        print('select negociospush_process')
        cur.execute(query_codes)
        query_results = cur.fetchall()
        print(cur.rowcount)
        for row in query_results:
            id_process = row['IdProcess']
            query = """
                    SELECT DISTINCT "ProductCode_id"/100 as "ClassCode_id", "User_id" FROM public.negociospush_usercode
                    WHERE "ProductCode_id"/100 = %s;
                    """
            # print('select negociospush_usercode')
            cur.execute(query, (int(row['ClassCode']),))
            codes = cur.fetchall()
            # print(codes)
            # print(cur.rowcount)
            for code in codes:
                user_id = int(code['User_id'])
                # Se crean las notificaciones en BD
                query_notifications = """
                                    SELECT id, message, read, sent, "SystemLoadDate", recipient_id
                                    FROM public.negociospush_notification WHERE NOT sent AND recipient_id = %s ORDER BY 
                                    id DESC;
                                    """
                # print('select negociospush_notification user', user_id)
                cur.execute(query_notifications, (user_id,))
                # print('afterExcecute rowcount', cur.rowcount)
                notifs = cur.fetchall()
                if cur.rowcount == 0:
                    insert_notifications_query = """
                                                INSERT INTO public.negociospush_notification(
                                                message, read, sent, "SystemLoadDate", recipient_id)
                                                VALUES (%s, %s, %s, %s, %s) RETURNING id;
                                                """
                    dt = datetime.now()
                    # print('Insert negociospush_notification')
                    cur.execute(insert_notifications_query, (
                        "Tienes procesos relacionados a tu actividad económica que fueron convocados recientemente",
                        False,
                        False, dt, user_id))
                    notifs = cur.fetchall()
                # print(cur.rowcount)
                dt = datetime.now()
                notification_id = ""
                for notif in notifs:
                    notification_id = notif['id']
                insert_notifications_detail_query = """
                                                    INSERT INTO public.negociospush_notificationprocesses(
                                                    "SystemLoadDate", parent_id, process_id)
                                                    VALUES (%s, %s, %s);
                                                    """
                # print('Insert negociospush_notificationprocesses')
                cur.execute(insert_notifications_detail_query, (dt, notification_id, id_process))
        connection.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        # exc_type, exc_obj, exc_tb = sys.exc_info()
        # fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        # print(exc_type, fname, exc_tb.tb_lineno)
        raise error
    finally:
        if connection is not None:
            connection.close()


def enviar_correos():
    # print('Inicia')
    try:
        connection = psycopg2.connect(host=os.environ['HOSTDB'], port=os.environ['PORTDB'],
                                      database=os.environ['NAMEDB'], user=os.environ['USERDB'],
                                      password=os.environ['PASSDB'])
        cur = connection.cursor(cursor_factory=RealDictCursor)
        query_notifications = """
                    SELECT n.id, n.message, u.first_name, u.last_name, u.email
                    FROM public.negociospush_notification n 
                    INNER JOIN public.auth_user u on n.recipient_id = u.id 
                    WHERE NOT sent;
                    """
        # print('select negociospush_notification')
        cur.execute(query_notifications)
        notifications = cur.fetchall()
        for notif in notifications:
            recip = notif['email']
            mess = notif['message']
            name = notif['first_name'] + ' ' + notif['last_name']
            notification_id = notif['id']
            query_notifications_processes = """
                    SELECT p."EntityName", p."ProcessNumber", p."ExecutionCity", p."Description", p."Amount" 
                    FROM public.negociospush_notificationprocesses n
                    INNER JOIN public.negociospush_process p on n.process_id = p."IdProcess"
                    WHERE n.parent_id = %s limit 3
                    """
            cur.execute(query_notifications_processes, (notification_id,))
            notif_proc = cur.fetchall()
            text_processes = ""
            html_processes = "<ul style=\"list-style: none;\">"
            for notproc in notif_proc:
                entity = notproc['EntityName']
                process_number = notproc['ProcessNumber']
                cities = notproc['ExecutionCity']
                description = notproc['Description']
                amount = str(notproc['Amount'])
                html_processes += f"""
                                <li>
                                    <ul style="list-style: none;">
                                        <li>Número del proceso {process_number}</li>
                                        <li>Convocado por la entidad {entity}</li>
                                        <li>A ser ejecutado en {cities}</li>
                                        <li>{description}</li>
                                        <li>Cuantía {amount}</li>
                                    </ul>
                                </li>
                                <br/>
                                """
                text_processes += f"""
                                -Número del proceso {process_number} \r\n
                                Convocado por la entidad {entity} \r\n
                                A ser ejecutado en {cities} \r\n
                                {description} \r\n
                                Cuantía {amount} \r\n
                                \r\n
                                """
            html_processes += "<li>Entre otros más...</li></ul>"
            body_text = (f""" Estimad@ {name} \r\n
                        {mess} \r\n
                        {text_processes} \r\n
                        Entre otros más... \r\n
                        Ingresa a nuestra pagina para más información. Utilizando este enlace 
                        http://ec2-3-88-210-160.compute-1.amazonaws.com \r\n \r\n
                        Este correo es generado automaticamente con Amazon SES
                        """
                         )

            # The HTML body of the email.
            body_html = f"""<html>
                            <head></head>
                            <body>
                                <h3>Estimad@ {name}</h3>
                                <p>{mess}</p>
                                {html_processes}
                                <h4>Ingresa a nuestra <a href="http://ec2-3-88-210-160.compute-1.amazonaws.com/">página
                                </a> para más información</h4>
                                <p>Este correo es generado automaticamente
                                <a href='https://aws.amazon.com/ses/'>Amazon SES</a></p>
                            </body>
                            </html>
                        """
            send_email(recip, body_text, body_html)
            # Se crean las notificaciones en BD
            query_update_sent = """
                                UPDATE public.negociospush_notification SET sent=true
                                WHERE id = %s;
                                """
            cur.execute(query_update_sent, (notification_id,))
        connection.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        # exc_type, exc_obj, exc_tb = sys.exc_info()
        # fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        #  print(exc_type, fname, exc_tb.tb_lineno)
        raise error
    finally:
        if connection is not None:
            connection.close()


def send_email(recipient, body_text, body_html):
    # print('Se envía correo a utilizando SES')
    # Replace sender@example.com with your "From" address.
    # This address must be verified with Amazon SES.
    sender = "Negocios Push <negociospush@gmail.com>"

    # If necessary, replace us-west-2 with the AWS Region you're using for Amazon SES.
    aws_region = "us-east-1"

    # The subject line for the email.
    subject = "Nuevos procesos convocados"

    # The character encoding for the email.
    charset = "UTF-8"

    # Create a new SES resource and specify a region.
    client = boto3.client('ses',
                          region_name=aws_region,
                          aws_access_key_id=os.environ['SESKEYID'],
                          aws_secret_access_key=os.environ['SESSECRETKEY'])
    # Try to send the email.
    try:
        # Provide the contents of the email.
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    recipient,
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': charset,
                        'Data': body_html,
                    },
                    'Text': {
                        'Charset': charset,
                        'Data': body_text,
                    },
                },
                'Subject': {
                    'Charset': charset,
                    'Data': subject,
                },
            },
            Source=sender,
        )
    # Display an error if something goes wrong.
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])


# connection = psycopg2.connect(host="localhost", database="suppliers", user="postgres", password="postgres")
sched = BlockingScheduler()


@sched.scheduled_job('cron', hour=1, minute=21)
def scheduled_job():
    print('Tarea programada diariamente a la 1:30am')
    crear_notificaciones()
    enviar_correos()


sched.start()
