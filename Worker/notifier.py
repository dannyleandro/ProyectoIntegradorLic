import sys, os
import psycopg2
from apscheduler.schedulers.blocking import BlockingScheduler
from psycopg2.extras import RealDictCursor
from datetime import datetime
import boto3
from botocore.exceptions import ClientError
from apscheduler.schedulers.blocking import BlockingScheduler


def crearNotificaciones():
    print('Inicia')
    try:
        conn = psycopg2.connect(host=os.environ['HOSTDB'], port=os.environ['PORTDB'], database=os.environ['NAMEDB'],
                                user=os.environ['USERDB'], password=os.environ['PASSDB'])
        cur = conn.cursor(cursor_factory=RealDictCursor)
        queryCodes = """
                    SELECT "IdProcess", "ClassCode" FROM public.negociospush_process
                    WHERE "SystemLoadDate" > now() - INTERVAL '1 day' limit 10
                    """
        print('select negociospush_process')
        cur.execute(queryCodes)
        query_results = cur.fetchall()
        print(cur.rowcount)
        for row in query_results:
            IdProcess = row['IdProcess']
            lowerProductCode = int(row['ClassCode']) * 100
            upperProductCode = (int(row['ClassCode']) + 1) * 100
            query = """
                    SELECT "ProductCode_id", "User_id" FROM public.negociospush_usercode 
                    WHERE "ProductCode_id">=%s and "ProductCode_id"<%s;
                    """
            print('select negociospush_usercode')
            cur.execute(query, (lowerProductCode, upperProductCode))
            codes = cur.fetchall()
            # print(codes)
            print(cur.rowcount)
            for code in codes:
                user_id = int(code['User_id'])
                # Se crean las notificaciones en BD
                queryNotifications = """
                                    SELECT id, message, read, sent, "SystemLoadDate", recipient_id
                                    FROM public.negociospush_notification WHERE NOT sent AND recipient_id = %s ORDER BY id DESC;
                                    """
                print('select negociospush_notification')
                cur.execute(queryNotifications, (user_id,))
                if cur.fetchone() is None:
                    insert_notifications_query = """
                                                INSERT INTO public.negociospush_notification(
                                                message, read, sent, "SystemLoadDate", recipient_id)
                                                VALUES (%s, %s, %s, %s, %s) RETURNING id;
                                                """
                    dt = datetime.now()
                    print('Insert negociospush_notification')
                    cur.execute(insert_notifications_query, (
                    "Tienes procesos relacionados a tu actividad económica que fueron convocados recientemente", False,
                    False, dt, user_id))
                notifs = cur.fetchall()
                print(cur.rowcount)
                for notif in notifs:
                    notification_id = notif['id']
                insert_notifications_detail_query = """
                                                    INSERT INTO public.negociospush_notificationprocesses(
                                                    "SystemLoadDate", parent_id, process_id)
                                                    VALUES (%s, %s, %s);
                                                    """
                print('Insert negociospush_notificationprocesses')
                cur.execute(insert_notifications_detail_query, (dt, notification_id, IdProcess))
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        # exc_type, exc_obj, exc_tb = sys.exc_info()
        # fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        # print(exc_type, fname, exc_tb.tb_lineno)
        raise error
    finally:
        if conn is not None:
            conn.close()


def enviarCorreos():
    print('Inicia')
    try:
        conn = psycopg2.connect(host=os.environ['HOSTDB'], port=os.environ['PORTDB'], database=os.environ['NAMEDB'],
                                user=os.environ['USERDB'], password=os.environ['PASSDB'])
        cur = conn.cursor(cursor_factory=RealDictCursor)
        queryNotifications = """
                    SELECT n.id, n.message, u.first_name, u.last_name, u.email --message, read, sent, "SystemLoadDate", recipient_id, 
                    FROM public.negociospush_notification n 
                    INNER JOIN public.auth_user u on n.recipient_id = u.id 
                    WHERE NOT sent;
                    """
        print('select negociospush_notification')
        cur.execute(queryNotifications)
        notifications = cur.fetchall()
        for notif in notifications:
            recip = notif['email']
            mess = notif['message']
            name = notif['first_name'] + ' ' + notif['first_name']
            notification_id = notif['id']
            queryNotificationsProcesses = """
                    SELECT p."EntityName", p."ProcessNumber", p."ExecutionCity", p."Description", p."Amount" FROM public.negociospush_notificationprocesses n
                    INNER JOIN public.negociospush_process p on n.process_id = p."IdProcess"
                    WHERE n.parent_id = %s limit 3
                    """
            cur.execute(queryNotificationsProcesses, (notification_id,))
            notifProc = cur.fetchall()
            textProcesses = ""
            htmlProcesses = "<br/><br/><ul>"
            for notproc in notifProc:
                entity = notproc['EntityName']
                processNumber = notproc['ProcessNumber']
                cities = notproc['ExecutionCity']
                description = notproc['Description']
                amount = str(notproc['Amount'])
                htmlProcesses += """
                                <br/>
                                <li>Número del proceso """ + processNumber + """</li>
                                <li>Convocado por la entidad """ + entity + """</li>
                                <li>A ser ejecutado en """ + cities + """</li>
                                <li>""" + description + """</li>
                                <li>Cuantía """ + amount + """</li>
                                <br/>
                                """
                textProcesses += """
                                -Número del proceso """ + processNumber + """ \r\n
                                Convocado por la entidad """ + entity + """ \r\n
								 A ser ejecutado en """ + cities + """ \r\n
								 """ + description + """ \r\n
								 Cuantía """ + amount + """ \r\n
								 \r\n
								 \r\n
								 """
            htmlProcesses += "</ul><br/><br/>"
            BODY_TEXT = (""" Estimad@ """ + name + """ \r\n
	             		""" + mess + """ \r\n
	             		""" + textProcesses + """\r\n
	             		Ingresa a nuestra pagina para más información. \r\n \r\n
		 	            Este correo es generado automaticamente con Amazon SES
	            		"""
                         )

            # The HTML body of the email.
            BODY_HTML = """<html>
							<head></head>
							<body>
							  <h2>Estimad@ """ + name + """</h2>
							  <h3>""" + mess + """</h3>
							  """ + htmlProcesses + """
							  <h3>Ingresa a nuestra pagina para más información</h3>
						  	  <p>Este correo es generado automaticamente
						      <a href='https://aws.amazon.com/ses/'>Amazon SES</a></p>
							</body>
						</html>
						"""
            sendEmail(recip, BODY_TEXT, BODY_HTML)
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        # exc_type, exc_obj, exc_tb = sys.exc_info()
        # fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        #  print(exc_type, fname, exc_tb.tb_lineno)
        raise error
    finally:
        if conn is not None:
            conn.close()


def sendEmail(RECIPIENT, BODY_TEXT, BODY_HTML):
    print('Se envía correo a utilizando SES')
    # Let's use Amazon S3
    s3 = boto3.resource('s3')
    # Replace sender@example.com with your "From" address.
    # This address must be verified with Amazon SES.
    SENDER = "Negocios Push <dannylhurtado@gmail.com>"

    # If necessary, replace us-west-2 with the AWS Region you're using for Amazon SES.
    AWS_REGION = "us-east-1"

    # The subject line for the email.
    SUBJECT = "Nuevos procesos convocados"

    # The character encoding for the email.
    CHARSET = "UTF-8"

    # Create a new SES resource and specify a region.
    client = boto3.client('ses',
                          region_name=AWS_REGION,
                          aws_access_key_id=os.environ['SESKEYID'],
                          aws_secret_access_key=os.environ['SESSECRETKEY'])
    # Try to send the email.
    try:
        # Provide the contents of the email.
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    RECIPIENT,
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': BODY_HTML,
                    },
                    'Text': {
                        'Charset': CHARSET,
                        'Data': BODY_TEXT,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': SUBJECT,
                },
            },
            Source=SENDER,
            # If you are not using a configuration set, comment or delete the
            # following line
        )
    # Display an error if something goes wrong.
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])


conn = psycopg2.connect(host="localhost", database="suppliers", user="postgres", password="postgres")
sched = BlockingScheduler()


@sched.scheduled_job('cron', hour=1, minute=30)
def scheduled_job():
    print('Tarea programada diariamente a la 1:30am')
    crearNotificaciones()
    enviarCorreos()


sched.start()
