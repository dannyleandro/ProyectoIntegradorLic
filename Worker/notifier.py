import sys, os
import psycopg2
from apscheduler.schedulers.blocking import BlockingScheduler
from psycopg2.extras import RealDictCursor
from datetime import datetime

def app():
	print('Inicia')
	try:
		conn = psycopg2.connect(host=os.environ['HOSTDB'], port = os.environ['PORTDB'], database=os.environ['NAMEDB'], user=os.environ['USERDB'], password=os.environ['PASSDB'])
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
			lowerProductCode = int(row['ClassCode'])*100
			upperProductCode = (int(row['ClassCode'])+1)*100
			query  = """
					SELECT "ProductCode_id", "User_id" FROM public.negociospush_usercode 
					WHERE "ProductCode_id">=%s and "ProductCode_id"<%s;
					"""
			print('select negociospush_usercode')
			cur.execute(query, (lowerProductCode, upperProductCode))
			codes = cur.fetchall()
			# print(codes)
			print(cur.rowcount)
			for code in codes:
				user_id=int(code['User_id'])
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
					cur.execute(insert_notifications_query, ("Tienes procesos relacionados a tu actividad económica que fueron convocados recientemente", False, False, dt, user_id))
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
app()

# from apscheduler.schedulers.blocking import BlockingScheduler

# conn = psycopg2.connect(host="localhost",database="suppliers", user="postgres", password="postgres")
# sched = BlockingScheduler()

# @sched.scheduled_job('cron', hour=1, minute=30)
# def scheduled_job():
#     print('This job is run every weekday at 10am.')
# 	os.environ['NAMEDB']


# sched.start()