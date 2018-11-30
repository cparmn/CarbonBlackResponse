
sensor_obj = cb.select(Sensor).where("ip:x.x.x").first()


with cb.select(Sensor, 50).lr_session() as lr_session:
	for entry in lr_session.walk("c:\users"):
		print(entry)


with cb.select(Sensor, 50).lr_session() as lr_session:
	print(lr_session.create_process(r'cmd.exe /c "ping.exe 8.8.8.8"'))


with cb.select(Sensor, 50).lr_session() as lr_session:
	print(lr_session.create_process(r'tasklist /v"'))
	print(lr_session.create_process(r'ipconfig /displaydns"'))
	print(lr_session.create_process(r'query session"'))
