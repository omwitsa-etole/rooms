from flask import Flask, render_template, request, redirect, url_for, session, abort, flash
import random
import mysql.connector
import datetime
import webbrowser
import socket
import sys
import random
import mysql.connector
import datetime
import webbrowser
import socket
#from werkzeug import secure_filename
#import vonage
from datetime import date
from datetime import timedelta
from cryptography.fernet import Fernet
from mail import *
from datetime import date

app = Flask(__name__)
app.debug = True
app.secret_key = 'app@BlogSpot'


def connector():
	"""
	db = mysql.connector.connect(host="localhost",    # your host, usually localhost
                     user="root",         # your username
                     passwd="root",  # your password
                     db="dbo")
	"""
	for i in range(0,8):
		try:
			db = mysql.connector.connect(host="192.185.81.65",    # your host, usually localhost
		             user="askabcry_admim",         # your username
		             passwd="tryandhackme",  # your password
		             db="askabcry_rooms")
			break
		except Exception as e:
			print(str(e))
			pass
#	"""
	if db == None:
		raise "No connection"

	return db

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route("/api/v1/request/<mode>", methods=['GET','POST'])
def Api(mode):
	if mode == "createGroup":
		msg = "Anauthorised request"
		if session.get("rooms-user") != None and session.get("room-name") != None:
			if request.method == "POST" and "key" in request.form:
				msg = "Not Finished"
				try:
					#print(request.form)
					key = Fernet.generate_key()
					name = request.form["name"]
					topic = request.form["topic"]
					description = request.form["description"]
					profile = request.form["profile"]
					if profile == "private":
						profile = "1"
					else:
						profile = "0"
					participants = request.form.getlist("participants[]")
					try:
						while True:
							try:
								db = connector()
								break
							except:
								pass
						cur = db.cursor(buffered=True)
						cur.execute("select * from group_rooms where key_ID=%s",(key,))
						exists = cur.fetchone()
						if exists:
							return "An error has occured kindly try again"
						cur.execute("select key_ID from users where email_id=%s and name=%s",(session["rooms-user"],session["room-name"],))
						user_key = cur.fetchone()
						cur.execute("insert into group_rooms(key_ID,name,restricted,title,description,creator_ID) values(%s,%s,%s,%s,%s,%s)",(key, name,profile,topic,description,user_key[0],))
						cur.execute("insert into group_members(group_ID,key_ID,name) values(%s, %s,%s)",(key,user_key[0],session["room-name"],))
						for user in participants:
							if user != "" and user != None:
								if not db:
									while True:
										try:
											db = connector()
											break
										except:
											pass
									cur = db.cursor(buffered=True)
								cur.execute("select name from users where key_ID=%s",(user,))
								nm = cur.fetchone()
								cur.execute("insert into group_members(group_ID, key_ID,name) values(%s,%s,%s)",(key,user,nm[0],))
						msg = "success"
					except Exception as e:
						print(str(e))
						db.rollback()
						pass
					finally:
						db.commit()
						db.close()
				except Exception as e:
					print(str(e))
					msg ="An unknown error has occured"
					pass
		return msg
	if mode == "deleteChat":
		msg = "Anauthorised request"
		if request.method == "POST" and "key" in request.form:
			msg = "Not Finished"
			if session.get("active") != None and session.get("rooms-user") != None and session.get("room-name") != None:
				active = session["active"]
				try:
					while True:
						try:
							db = connector()
							break
						except:
							pass
					cur = db.cursor(buffered=True)
					cur.execute("select key_ID from users where email_id=%s and name=%s", (session["rooms-user"],session["room-name"],))
					key = cur.fetchone()
					cur.execute("select key_ID from users where email_id=%s or name=%s",(active,active,))
					eid = cur.fetchone()
					if eid:
						cur.execute("update room_messages set message='deleted' where id=%s and reciever_id=%s",(key[0],eid[0],))
						msg = "success"
				except:
					msg = "An Error Occured during the Transaction"
					db.rollback()
					pass
				finally:
					db.commit()
					db.close()
		return msg
	if mode == "deleteMsg":
		msg = "Anauthorised"
		if request.method == "POST" and "key" in request.form and "id" in request.form:
			msg = "Not Finished"
			index = request.form["id"]
			if session.get("room-name") != None and session.get("rooms-user") != None:
				try:
					while True:
						try:
							db = connector()
							break
						except:
							pass
					cur = db.cursor(buffered=True)
					cur.execute("select message from room_messages where ind=%s",(index,))
					mess = cur.fetchone()
					if mess[0] == "deleted":
						cur.execute("delete from room_messages where ind=%s",(index,))
						msg = "successfull"
					else:
						cur.execute("update room_messages set message='deleted' where ind=%s", (index,))
						msg = "success"
				except Exception as e:
					msg = "An error occured during the transaction"
					print(str(e))
					db.rollback()
					pass
				finally:
					db.commit()
					db.close()
		return msg
	if mode == "join-room":
		msg = "Anauthorised request"
		if request.method == 'POST' and 'email' in request.form and "key" in request.form:
			msg = "error during transaction"
			email = request.form["email"]
			name = request.form["uname"]
			if email == "":
				return "Email input required"
			key = Fernet.generate_key()
			verificationcode = random.randint(100000, 999999)
			code = verificationcode
			try:
				while True:
					try:
						db = connector()
						break
					except:
						pass
				cur = db.cursor(buffered=True)

				cur.execute('SELECT * FROM users WHERE email_id=%s', (email, ))
				exists = cur.fetchone()
				if exists:
					return "User With email "+email+" already Registered"
				cur.execute('SELECT * FROM users WHERE name=%s', (name, ))
				exists = cur.fetchone()
				if exists:
					return "Username "+name+" not available"
				cur.execute('SELECT * FROM rooms WHERE email_id=%s', (email, ))
				exists = cur.fetchone()
				if exists:
					return "User With email "+email+" already Registered"
				cur.execute('SELECT * FROM rooms WHERE name=%s', (name, ))
				exists = cur.fetchone()
				if exists:
					return "Username "+name+" not available"
				cur.execute('INSERT INTO rooms (email_id, verification, name,dkey) VALUES(%s, %s, %s,%s)', (email, str(code), name, key, ))
				msg ="success"
			except Exception as e:
				db.rollback()
				print(str(e))
				pass	
			finally:
				db.commit()
				db.close()
			try:
				while True:
					try:
						db = connector()
						break
					except:
						pass
				cur = db.cursor(buffered=True)

				cur.execute('SELECT verification FROM rooms WHERE email_id=%s and dkey=%s', (email, key, ))
				code = cur.fetchone()
				if code:
					msg = mail(email, str(code[0]))
			except Exception as e:
				msg = "Error occured during transaction"
				db.rollback()
				print(str(e))
				pass
			finally:
				db.close()
		return msg
	if mode=="verify":
		msg = "Not finished"
		if request.method == 'POST' and 'email' in request.form and 'code' in request.form:
			email = request.form["email"]
			code = request.form["code"]
			
			if email == "" or code == "":
				return "Invalid values"
			try:
				while True:
					try:
						db = connector()
						break
					except:
						pass
				cur = db.cursor(buffered=True)

				cur.execute('SELECT * FROM rooms WHERE email_id=%s and verification=%s', (email, code, ))
				exists = cur.fetchone()
				
				if exists:
					cur.execute("update rooms set verification='' WHERE email_id=%s and verification=%s",(email,code,))
					cur.execute('INSERT INTO users (key_ID, email_id, name) VALUES(%s, %s, %s)', (exists[4], exists[0], exists[3], ))
					cur.execute("insert into profile (key_ID,email_id,name) VALUES(%s, %s, %s)",(exists[4], exists[0], exists[3], ))
					cur.execute("insert into profile_links (key_ID) values(%s)",(exists[4],))
					session["loggedin"] = "user"
					session["rooms-user"] = exists[0]
					session["room-name"] = exists[3]
					return "success"
				else:
					return "Code not valid"
			except Exception as e:
				msg = "Error occured during transaction"
				db.rollback()
				print(str(e))
				pass
			finally:
				db.commit()
				db.close()
		return msg
	if mode=="login":
		msg = "Not finished"
		if request.method == 'POST' and 'email' in request.form and 'code' in request.form:
			email = request.form["email"]
			code = request.form["code"]
			
			if email == "" or code == "":
				return "Invalid values"
			try:
				while True:
					try:
						db = connector()
						break
					except:
						pass
				cur = db.cursor(buffered=True)

				cur.execute('SELECT * FROM rooms WHERE email_id=%s and verification=%s', (email, code, ))
				exists = cur.fetchone()
				if exists:
					
					session["loggedin"] = "user"
					session["rooms-user"] = exists[0]
					session["room-name"] = exists[3]
					return "success"
				else:
					return "Code not valid"
			except Exception as e:
				msg = "Error occured during transaction"
				db.rollback()
				print(str(e))
				pass
			finally:
				db.commit()
				db.close()
		return msg
	if mode == "getCode":
		mssg = "Request not Finished"
		if request.method == 'POST' and 'email' in request.form and "key" in request.form:
			email = request.form["email"]
			verificationcode = random.randint(100000, 999999)
			code = verificationcode
			print(code)
			try:
				while True:
					try:
						db = connector()
						break
					except:
						pass
				cur = db.cursor(buffered=True)

				cur.execute('update rooms set verification=%s WHERE email_id=%s', (str(code),email, ))
				try:
					msg = mail(email, str(code))
				except:
					pass
				mssg= "success"
			except Exception as e:
				mssg = "Error occured during transaction"
				db.rollback()
				print(str(e))
				pass
			finally:
				db.commit()
				db.close()
			
		return mssg
	if mode == "connect":
		recieved = request.args.get("outgoing")
		end = request.args.get("endcall")
		if session.get("rooms-user")!= None and session.get("room-name") != None and session.get("active")!=None:
			user =session["rooms-user"]
			caller = session["active"]
			msg= "call not finished"
			if request.method == "POST" and "key" in request.form:
				try:
					while True:
						try:
							db = connector()
							break
						except:
							pass
					cur = db.cursor(buffered=True)
					cur.execute("select key_ID from users where email_id=%s and name=%s",(user,session["room-name"],))
					user_key = cur.fetchone()
					cur.execute("select key_ID from users where email_id=%s or name=%s",(caller,caller,))
					active_key = cur.fetchone()
					if end == None and recieved == None:
						cur.execute("update users set on_call='1' where email_id =%s or name=%s",(caller,caller,))
						cur.execute("insert into call_connections(caller_id,reciever_id) values(%s,%s)", (active_key[0],user_key[0], ))
						msg = "success"
					if end == "outgoing":
						cur.execute("update users set on_call='0' where email_id =%s or name=%s",(caller,caller,))
						cur.execute("insert into call_connections(caller_id,reciever_id) values(%s,%s)", (active_key[0],user_key[0], ))
						session['on-cal'] = None
						msg = "success"
					if end =="incoming":
						cur.execute("insert into call_connections(caller_id,reciever_id) values(%s,%s)", (active_key[0],user_key[0], ))
						cur.execute("update users set on_call='0' where email_id =%s and name=%s",(user,session["room-name"],))
						msg  = "success"
					if recieved != None:
						session["on-cal"] = True
						
						msg="success"
					if session.get("on-cal") == None:
						
						cur.execute("insert into call_connections(caller_id,reciever_id) values(%s,%s)", (user_key[0],active_key[0], ))
						msg="success"
				
				except Exception as e:
					msg = "Error"
					db.rollback()
					print(str(e))
					pass
				finally:
					db.commit()
					db.close()
			return msg

@app.route("/api/v/request/<mode>", methods=['GET', 'POST'])
def ApiRoom(mode):
	if mode == "checkRoom":
		msg = ["false", "false","None"]
		if session.get("active")=="None":
			session["active"] = None
		if session.get("room-name") != None and session.get("room-name") != "NULL" and session.get("rooms-user") != None:
			user = session.get("room-name")
			active = session.get("active")
			if user != None:
				msg[0] = "false"
				messages = []
				if user != None:
					try:
						while True:
							try:
								db = connector()
								break
							except:
								pass
						cur = db.cursor(buffered=True)
						cur.execute('update users set last_online=current_timestamp where email_id=%s and name=%s', (session["rooms-user"],session["room-name"],))
						cur.execute('SELECT has_new FROM users WHERE email_id=%s and name=%s', (session["rooms-user"], user, ))
						eid = cur.fetchone()
						if eid and eid[0] == 1 or eid[0] == '1':
							cur.execute('update users set has_new="0" where email_id=%s and name=%s', (session["rooms-user"], user,))
							msg[0] = "true"
						cur.execute("select on_call,caller_id from users where email_id=%s and name=%s",(session["rooms-user"],session["room-name"],))
						calling = cur.fetchone()
						if calling and calling[0] == 1 or calling[0] =="1":
							if session.get("on-cal") != True:
								msg[1] ="true"
								cur.execute("select name from users where key_ID=%s",(calling[1],))
								msg[2] = cur.fetchone()[0]
								session["active"] = msg[2]
					except Exception as e:
						db.rollback()
						print(str(e))
						pass
					finally:
						db.commit()
						db.close()
			"""
			if active != None:
				from_user = session["room-name"]
				msg[1] = "false"
				try:
					while True:
						try:
							db = connector()
							break
						except:
							pass
					cur = db.cursor(buffered=True)
					cur.execute('SELECT * FROM users WHERE email_id=%s and name=%s', (session["rooms-user"], from_user, ))
					eid = cur.fetchone()
					cur.execute("select * from users where email_id=%s or name=%s",(active,active,))
					eiid = cur.fetchone()
					
					if eid and eiid:
						cur.execute('SELECT * FROM room_messages WHERE id=%s and reciever_id=%s and is_read=0', (eid[0], eiid[0], ))
						eid = cur.fetchone()
						if eid:
							cur.execute("UPDATE room_messages SET is_read='1' where from_user=%s and to_user=%s", (from_user,active,))
							msg[1] = "true"
							
				except Exception as e:
					db.rollback()
					print(str(e))
					pass
				finally:
					db.commit()
					db.close()
			
			if session.get('active-group') != None:
				msg[1] = "false"
				try:
					while True:
						try:
							db = connector()
							break
						except:
							pass
					cur = db.cursor(buffered=True)
					cur.execute("select key_ID from users where email_id=%s and name=%s",(session["rooms-user"],session["room-name"],))
					user_key = cur.fetchone()
					cur.execute('SELECT * FROM group_messages WHERE id=%s and key_ID=%s and is_read="0" or is_read="0"', (session["active-group"],user_key[0], ))
					eid = cur.fetchone()
					if eid:
						cur.execute("update group_messages set is_read=1 where id=%s and key_ID=%s",(session["active-group"],user_key[0],))
						msg[1] = "true"
							
				except Exception as e:
					db.rollback()
					print(str(e))
					pass
				finally:
					db.commit()
					db.close()
			"""
				
		return msg[0]+","+msg[1]+","+msg[2]
	if mode == "checkMessage":
		msg = "false"
		active = request.args.get("active")
		if active != None:
			session["active"] = active
			session["active-group"] = None
			msg = "true"
		"""
		if session.get("room-name") != None and session.get("room-name") != "NULL" and session.get("rooms-user") != None:
			user = session["room-name"]
			if user != None:
				messages = []
				if user != None:
					try:
						while True:
							try:
								db = connector()
								break
							except:
								pass
						cur = db.cursor(buffered=True)
						cur.execute('SELECT has_new FROM users WHERE email_id=%s or name=%s', (user, user, ))
						eid = cur.fetchone()
						if eid[0] == 1 or eid[0] == '1':
							cur.execute('update users set has_new="0" where email_id=%s or name=%s', (user, user,))
							msg = "true"
					except Exception as e:
						db.rollback()
						print(str(e))
						pass
					finally:
						db.commit()
						db.close()
		"""
		return msg
	if mode == "loadmessages":
		
		chats = request.args.get("archived")
		last_online = datetime.datetime.now() - timedelta(minutes=2)
		if session.get("room-name") != None and session.get("room-name") != "NULL" and session.get("rooms-user") != None:
			user = session["room-name"]
			if user != None:
				messages = []
				get_users=[]
				if user != None:
					try:
						while True:
							try:
								db = connector()
								break
							except:
								pass
						cur = db.cursor(buffered=True)
						cur.execute('SELECT * FROM users WHERE email_id=%s or name=%s', (user, user, ))
						eid = cur.fetchone()
						if eid:
							cur.execute('SELECT * FROM room_messages WHERE id=%s or reciever_id=%s ORDER BY time DESC', (eid[0], eid[0], ))
							messages = cur.fetchall()
							for message in messages:
								cur.execute("select name from users where key_ID=%s",(message[0],))
								name=cur.fetchone()[0]
								cur.execute("select name from users where key_ID=%s",(message[6],))
								name2=cur.fetchone()[0]	
								get_users.append([name,name2])
							
						n = len(messages)
						
						#print(get_users)		
					except Exception as e:
						db.rollback()
						print(str(e))
						pass
					finally:
						db.close()
			my_groups = []
			my_group_messages = []
			if session.get("rooms-user") != None and session.get("room-name") != None:
				try:
					while True:
						try:
							db = connector()
							break
						except:
							pass
					cur = db.cursor(buffered=True)
					cur.execute("select key_ID from users where email_id=%s and name=%s",(session["rooms-user"],session["room-name"],))
					key = cur.fetchone()
					cur.execute("select group_ID from group_members where key_ID=%s",(key[0],))
					groups = cur.fetchall()
			
					for group in groups:
						if not db:
							while True:
								try:
									db = connector()
									break
								except:
									pass
							cur = db.cursor(buffered=True)
						cur.execute("select * from group_rooms where key_ID=%s",(group[0],))
						my_groups.append(cur.fetchone())
						cur.execute("select * from group_messages where id=%s order by time desc",(group[0],))
						my_group_messages.append(cur.fetchone())
					mn = len(groups)
				except Exception as e:
					print(str(e))
					pass
				finally:
					db.close()
		return render_template("load-messages.html", Fernet=Fernet, **locals())
	if mode == "loadroom":
		ddate = date.today()
		if session.get("room-name") != None and session.get("room-name") != "NULL":
			n = 0
			if session.get("active") != None:
				user = session["active"]
				from_user = session["room-name"]
				messages = []
				
				try:
					while True:
						try:
							db = connector()
							break
						except:
							pass
					cur = db.cursor(buffered=True)
					cur.execute('SELECT * FROM users WHERE email_id=%s or name=%s', (from_user, from_user, ))
					eid = cur.fetchone()
					if eid:
						cur.execute('SELECT * FROM users WHERE email_id=%s or name=%s', (user, user, ))
						eiid = cur.fetchone()
						if eiid:
							cur.execute('SELECT * FROM room_messages WHERE id=%s and reciever_id=%s or id=%s and reciever_id=%s', (eid[0], eiid[0], eiid[0], eid[0], ))
							messages = cur.fetchall()
					n = len(messages)
					
				except Exception as e:
					db.rollback()
					print(str(e))
					pass
				finally:
					db.close()
			if session.get("active-group") != None:
				group = session["active-group"]
				
				messages = []
				
				try:
					while True:
						try:
							db = connector()
							break
						except:
							pass
					cur = db.cursor(buffered=True)
					cur.execute("select key_ID from users where email_id=%s and name=%s",(session["rooms-user"],session["room-name"],))
					user_key = cur.fetchone()[0]
					cur.execute('SELECT * FROM group_messages WHERE id=%s', (group, ))
					messages = cur.fetchall()
					n = len(messages)
					
				except Exception as e:
					db.rollback()
					print(str(e))
					pass
				finally:
					db.close()
			return render_template("room-messages.html", Fernet=Fernet, **locals())
	if mode == "sendmessage":
		
		if session.get('room-name') != None or session.get('room-name') != "NULL" and session.get('rooms-user') != None :
			msg = "Anauthorised Request - 404 -"
			if session.get("active") != None and session.get("active") != "None":
				if request.method == 'POST' and 'msg' in request.form and "key" in request.form:
					to_user = session["active"]
					reciever = None
					msg = "transaction not complete"
					key = Fernet.generate_key()
					fernet = Fernet(key)
					user = session["room-name"]
					message = request.form['msg']
					encMessage = fernet.encrypt(message.encode())
					try:
						while True:
							try:
								db = connector()
								break
							except:
								pass
						cur = db.cursor(buffered=True)
						cur.execute('SELECT * FROM users WHERE email_id=%s or name=%s', (to_user, to_user, ))
						users = cur.fetchone()
						if users:
							receiver = users[1]
							cur.execute('SELECT * FROM users WHERE email_id=%s and name=%s', (session["rooms-user"], user, ))
							userss = cur.fetchone()
							if userss:
								cur.execute("select archived from room_messages where id=%s and reciever_id=%s",(userss[0],users[0],))
								arch = cur.fetchone()
								if arch:
									if arch[0] == '1' or arch[0] == 1:
										cur.execute('INSERT INTO room_messages (id, from_user,to_user,message, dkey, reciever_id,archived) VALUES(%s, %s,%s,%s, %s, %s,%s)', (userss[0], userss[0], users[0], encMessage, key, users[0], '1',))
									else:
										cur.execute('INSERT INTO room_messages (id, from_user, to_user, message, dkey, reciever_id) VALUES(%s, %s, %s, %s, %s, %s)', (userss[0], userss[0], users[0], encMessage, key, users[0], ))	
								
								
								msg = "success"
							else:
								msg = "The user "+str(user)+" has not registered in rooms"
						else:
							msg = "The user "+str(to_user)+" has not registered in rooms"		
										
					except Exception as e:
						msg = "An Error occured during the transaction"
						db.rollback()
						print(str(e))
						pass
					finally:
						db.commit()
						db.close()
				
				if "succ" in msg and receiver != None:
					try:
						while True:
							try:
								db = connector()
								break
							except:
								pass
						cur = db.cursor(buffered=True)
						cur.execute("update users set has_new=1 where email_id=%s or email_id=%s",(session["rooms-user"], receiver, ))
						
					except Exception as e:
						db.rollback();print("here")
						print(str(e))
						pass
					finally:
						db.commit()
						db.close()
					try:
						notify(reciever, session["room-name"], message, request.host)
					except Exception as e:
						print(str(e));print("here2")
						pass
				return msg
			if session.get("active-group") != None and session.get("active-group") != "None":
				if request.method == 'POST' and 'key' in request.form and 'msg' in request.form:
					reciever = None
					msg = "transaction not complete"
					to_group = session["active-group"]
					message = request.form["msg"]
					name = session["room-name"]
					key = Fernet.generate_key()
					fernet = Fernet(key)	
					encMessage = fernet.encrypt(message.encode())	
					try:
						while True:
							try:
								db = connector()
								break
							except:
								pass
						cur = db.cursor(buffered=True)
						cur.execute("select key_ID from users where email_id=%s and name=%s",(session["rooms-user"],session["room-name"],))
						user_key = cur.fetchone()
						cur.execute('SELECT key_ID FROM group_rooms WHERE key_ID=%s', (to_group, ))
						reciever = cur.fetchone()
						if reciever:
							cur.execute('INSERT INTO group_messages (id, key_ID, message, dkey, name) VALUES(%s,%s, %s, %s, %s)', (reciever[0],user_key[0], encMessage, key, name, ))	
							msg = "success"
							cur.execute("select key_ID from group_members where group_ID=%s",(reciever[0],))
							all_members = cur.fetchall()
							for member in all_members:
								if not db:
									while True:
										try:
											db = connector()
											break
										except:
											pass
									cur = db.cursor(buffered=True)
								cur.execute("update users set has_new='1' where key_ID=%s",(member[0],))
						else:
							msg = "Error! The group "+str(to_group)+" has not registered in rooms"				
					except Exception as e:
						msg = "An Error occured during the transaction"
						db.rollback()
						print(str(e))
						pass
					finally:
						db.commit()
						db.close()	
					if "succ" in msg and reciever != None:
						try:
							while True:
								try:
									db = connector()
									break
								except:
									pass
							cur = db.cursor(buffered=True)
							cur.execute("update group_rooms set has_new=1 where key_ID=%s",(reciever, ))
							
						except Exception as e:
							db.rollback()
							print(str(e))
							pass
						finally:
							db.commit()
							db.close()
				return msg
	if mode == "loadprofile":
		mine = request.args.get("mine")
		usr= request.args.get("user")
		if usr != None:
			if session.get("active") != None:
				email = session["active"]
				try:
					while True:
						try:
							db = connector()
							break
						except:
							pass
					cur = db.cursor(buffered=True)
					cur.execute('SELECT * FROM profile WHERE email_id=%s or name=%s', (email,email, ))
					user = cur.fetchone()
					if user:
						cur.execute('SELECT * FROM profile_links WHERE key_ID=%s', (user[0], ))
						links = cur.fetchone()
				except:
					pass
				finally:
					db.close()
		else:
			if session.get("rooms-user") != None:
				email = session["rooms-user"]
				try:
					while True:
						try:
							db = connector()
							break
						except:
							pass
					cur = db.cursor(buffered=True)
					cur.execute('SELECT * FROM profile WHERE email_id=%s or name=%s', (email,email, ))
					user = cur.fetchone()
					if user:
						cur.execute('SELECT * FROM profile_links WHERE key_ID=%s', (user[0], ))
						links = cur.fetchone()
				except:
					pass
				finally:
					db.close()
		
		return render_template("viewprofile.html", **locals())
	if mode=="getProfile":
		if session.get("rooms-user") != None:
			email = session["rooms-user"]
			try:
				while True:
					try:
						db = connector()
						break
					except:
						pass
				cur = db.cursor(buffered=True)
				cur.execute('SELECT * FROM profile WHERE email_id=%s or name=%s', (email,email, ))
				user = cur.fetchone()
				if user:
					cur.execute('SELECT * FROM profile_links WHERE key_ID=%s', (user[0], ))
					links = cur.fetchone()
			except:
				pass
			finally:
				db.close()
		return render_template("myprofile.html",**locals())
	if mode == "search-user":
		msg = "Anauthorised"
		if session.get('room-name') != None or session.get('room-name') != "NULL" and session.get('rooms-user') != None:
			if request.method=='POST' and "key" in request.form:
				msg = "Not finished"
				email = request.form["email"]
				try:
					while True:
						try:
							db = connector()
							break
						except:
							pass
					cur = db.cursor(buffered=True)
					cur.execute('SELECT * FROM users WHERE email_id=%s and name=%s', (session["rooms-user"],session["room-name"], ))
					key = cur.fetchone()
					cur.execute('SELECT * FROM users WHERE email_id=%s or name=%s', (email,email, ))
					eid = cur.fetchone()
					if eid:
						cur.execute("select * from contacts where key_ID=%s and contact_ID=%s", (key[0],eid[0],))
						exists = cur.fetchone()
						if exists:
							pass
						else:
							cur.execute("insert into contacts(key_ID, contact_ID) values(%s,%s)", (key[0],eid[0],))
						session["active"] = eid[2]
						msg = "success"
					else:
						msg = "No User(s) found"
				except:
					db.rollback()
					pass
				finally:
					db.commit()
					db.close()
		return msg
	if mode == "searchContacts":
		users = "success"
		if session.get("rooms-user") != None and session.get("room-name") != None:
			contact = request.args.get("contact")
			if contact != None:
				users = []
				contacts = "%"+contact+"%"
				try:
					while True:
						try:
							db = connector()
							break
						except:
							pass
					cur = db.cursor(buffered=True)
					cur.execute('SELECT key_ID FROM users WHERE email_id=%s and name=%s', (session["rooms-user"],session["room-name"], ))
					key = cur.fetchone()
					cur.execute('SELECT key_ID FROM users WHERE email_id like %s or name like %s', (contacts,contacts, ))
					eid = cur.fetchall()
					for e in eid:
						print(e[0])
						if not db:
							while True:
								try:
									db = connector()
									break
								except:
									pass
							cur = db.cursor(buffered=True)
						cur.execute('SELECT contact_ID FROM contacts WHERE key_ID = %s and contact_ID=%s', (key[0],e[0], ))
						conts = cur.fetchone()
						if conts:
							if not db:
								while True:
									try:
										db = connector()
										break
									except:
										pass
								cur = db.cursor(buffered=True)
							cur.execute('SELECT * FROM users WHERE key_ID = %s', (conts[0], ))
							users = cur.fetchall()
				except:
					#db.rollback()
					pass
				finally:
					db.close()
				n = len(users)
		return render_template("contacts-search.html", **locals())
	if mode == "archive":
		msg = "Anauthorised Request"
		if request.method=="POST" and "key" in request.form:
			msg = "Anauthorised"
			if session.get("active") !=  None:
				active = session["active"]
				msg = "Not Finished"
				try:
					while True:
						try:
							db = connector()
							break
						except:
							pass
					cur = db.cursor(buffered=True)
					cur.execute("select key_ID from users where email_id=%s and name=%s",(session["rooms-user"],session["room-name"],))
					key = cur.fetchone()
					cur.execute("select key_ID from users where email_id=%s or name=%s",(active,active,))
					eid = cur.fetchone()
					if eid:
						cur.execute("select archived from room_messages where id=%s and reciever_id=%s",(key[0],eid[0],))
						es = cur.fetchone()
						if es[0] == 1 or es[0] == '1':
							cur.execute("update room_messages set archived=0 where id=%s and reciever_id=%s",(key[0],eid[0],))
							msg = "successfull"
						else:
							cur.execute("update room_messages set archived=1 where id=%s and reciever_id=%s",(key[0],eid[0],))
							msg = "success"
				except Exception as e:
					msg = "Error occured during transaction";print(str(e))
					db.rollback()
					pass
				finally:
					db.commit()
					db.close()
		return msg
	if mode == "sendgroupmessage":
		
		if session.get('room-name') != None or session.get('room-name') != "NULL" and session.get("rooms-user") != None and session.get("active-group") != None:
			msg = "Anauthorised Request - 404 -"
			
		return msg
	if mode == "checkGroupMessage":
		msg = "fail"
		active = request.args.get("active")
		if active != None:
			msg = "success"
			session["active-group"] = active
			session["active"] = None
		return msg
	if mode == "chats":
		if session.get("rooms-user") != None and session.get("room-name") != None:
			return render_template("chats.html")
	if mode == "loadsupport":
		return render_template("support.html", **locals())
@app.route("/")
def red():
	return redirect("/room")
@app.route("/room/messager")
def getMessager():
	return render_template("messager.html")
@app.route("/room/header")
def getHeader():
	session["on-cal"]= None
	if session.get("active-group") != None:
		names = []
		try:
			while True:
				try:
					db = connector()
					break
				except:
					pass
			cur = db.cursor(buffered=True)
			cur.execute("select name from group_rooms where key_ID=%s",(session["active-group"],))
			name = cur.fetchone()[0]
			cur.execute("select * from group_members where group_ID=%s",(session["active-group"],))
			members = cur.fetchall()		
			n = len(members)
			cur.execute("select name from group_members where group_ID=%s",(session["active-group"],))
			ns = cur.fetchall()
			for nss in ns:
				names.append(nss[0])
		except:
			pass
		finally:
			db.close()
	return render_template("top-chat.html", **locals())

@app.route("/room/logout")
def logout():
	session.clear()
	return redirect("/")
@app.route("/room")
def rooms():
	signup = request.args.get("signup")
	password = request.args.get("forgot-password")
	if signup != None:
		return render_template("signup.html")
	if password != None:
		return render_template("forgot-password.html")
	if session.get("rooms-user") == None and session.get("room-name") == None:
		return render_template("login.html")
	
	chats = request.args.get("chats")
	groups = request.args.get("groups")
	status = request.args.get("status")
	settings = request.args.get("settings")
	calls = request.args.get("calls")
	index = request.args.get("index")
	if session.get("rooms-user") != None and session.get("room-name") != None:
		alphabet = ['A','B', 'C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
		email = session["rooms-user"]
		contacts = []
		try:
			while True:
				try:
					db = connector()
					break
				except:
					pass
			cur = db.cursor(buffered=True)
			cur.execute("select key_ID from users where email_id=%s and name=%s", (email, session["room-name"],))
			key = cur.fetchone()
			cur.execute('SELECT contact_ID FROM contacts where key_ID=%s', (key[0], ))
			users = cur.fetchall()
			for user in users:
				if not db:
					while True:
						try:
							db = connector()
							break
						except:
							pass
					cur = db.cursor(buffered=True)
				cur.execute("select * from users where key_ID=%s", (user[0],))
				contacts.append(cur.fetchone())
		except:
			pass
		finally:
			db.close()
	if groups != None:
		session["active"] = None
		session["groups"] = ""
		if session.get("rooms-user") != None and session.get("room-name") != None:
			try:
				while True:
					try:
						db = connector()
						break
					except:
						pass
				cur = db.cursor(buffered=True)
				cur.execute("select key_ID from users where email_id=%s and name=%s",(session["rooms-user"],session["room-name"],))
				user_key = cur.fetchone()
				cur.execute('SELECT group_ID FROM group_members WHERE key_ID=%s', (user_key[0], ))
				reciever = cur.fetchone()
				if reciever:
					session["active-group"] = reciever[0]
			except Exception as e:
				pass
			finally:
				db.close()
		return render_template("groups.html",Fernet=Fernet, **locals())
	if status != None:
		return render_template("status.html",**locals())
	if settings != None:
		email = session["rooms-user"]
		links=[]
		try:
			while True:
				try:
					db = connector()
					break
				except:
					pass
			cur = db.cursor(buffered=True)
			cur.execute('SELECT * FROM profile WHERE email_id=%s or name=%s', (email,email, ))
			user = cur.fetchone()
			if user:
				cur.execute('SELECT * FROM profile_links WHERE key_ID=%s', (userr[0], ))
				links = cur.fetchone()
		except:
			pass
		finally:
			db.close()
		return render_template("settings.html", **locals())
	if calls != None:
		
			
		return render_template("calls.html", **locals())
	else:
		session["groups"] = None
		return render_template("index.html",**locals())

@app.route("/room/settings")
def roomSettings():
	return redirect("/room?settings")

@app.route("/room/status")
def roomStatus():
	return redirect("/room?status")

@app.route("/room/groups")
def roomGroups():
	return redirect("/room?groups")

@app.route("/room/call")
def roomCalls():
	return redirect("/room?calls")

@app.route("/room/audio/call")
def audioCall():
	single = request.args.get("single")
	groups = request.args.get("group")
	if single != None:
		return render_template("audio_call.html")
	if groups != None:
		return render_template("audio_call_group.html")
	return render_template("audio_call.html")

@app.route("/room/video/call")
def videoCall():
	return render_template("video_call.html")

if __name__=="__main__":
	app.run("0.0.0.0")