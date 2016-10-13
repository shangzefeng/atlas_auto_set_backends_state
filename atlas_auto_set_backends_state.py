#coding: UTF-8


import MySQLdb 
import ConfigParser
import string, os, sys
import time
import logging


cf = ConfigParser.ConfigParser()
cf.read("setting.conf")

auto_switch_sleep_time = cf.get("auto_switch", "sleep_time")
log_path = cf.get("auto_switch", "log_path");

slave_db_host = cf.get("slave_db", "slave_db_host")
slave_db_user = cf.get("slave_db", "slave_db_user")
slave_db_pass = cf.get("slave_db", "slave_db_pass")
slave_db_port = cf.get("slave_db", "slave_db_port")

atlas_manage_host = cf.get("atlas_manage", "atlas_manage_host")
atlas_manage_user = cf.get("atlas_manage", "atlas_manage_user")
atlas_manage_pass = cf.get("atlas_manage", "atlas_manage_pass")
atlas_manage_port = cf.get("atlas_manage", "atlas_manage_port")

logging.basicConfig(level=logging.INFO,  
                    format='%(asctime)s %(levelname)s %(message)s',  
                    datefmt='%a, %d %b %Y %H:%M:%S', 
                    filename=log_path,
                    filemode='a+')  

class Slave:

  enable = True
  die = False

  def __init__(self, con='null', host='null'):
    self.con = con 
    self.host = host 

  def getCon(self):
    return self.con

  def getHost(self):
    return self.host 

slave_curs = []

hosts = slave_db_host.split(",")
    
slave_sql = 'show slave status'

atlas_con = MySQLdb.connect(host=atlas_manage_host, port=int(atlas_manage_port), user=atlas_manage_user, passwd=atlas_manage_pass)


for host in hosts:
  conn= MySQLdb.connect(host=host, port=int(slave_db_port), user=slave_db_user, passwd=slave_db_pass)
  slave_curs.append(Slave(conn, host));


def atlas_setoffline(slave_host):
  try:

    logging.info('slave host[' + slave_host+'] slave stop atlas set offline')

    cur = atlas_con.cursor()
    cur.execute('select * from backends')
    rows = cur.fetchall();

    for row in rows :
      backend_ndx = row[0]
      address = row[1].split(':')
      ip = address[0]

      if ip == slave_host and row[2] == 'up' :
        cur.execute('SET OFFLINE ' + str(backend_ndx))
        break

    cur.close()
    return

  except Exception, e:
    logging.info(str(e)) 
pass


def atlas_setonline(slave_host):
  try:

    cur = atlas_con.cursor()
    cur.execute('select * from backends')
    rows = cur.fetchall();

    for row in rows :
      backend_ndx = row[0]
      address = row[1].split(':')
      ip = address[0]

      if ip == slave_host and row[2] == 'offline' :
        cur.execute('SET ONLINE ' + str(backend_ndx))
        logging.info('slave host[' + slave_host+'] slave start atlas set online')
        break

    cur.close()
    return

  except Exception, e:
    logging.info(str(e))
pass


while True:
  index_list = []
  try :
    for slave_cur in slave_curs :

      if slave_cur.die:
        continue;

      ip = slave_cur.getHost()
      con = slave_cur.getCon()

      cur = con.cursor();
      cur.execute(slave_sql)
      row = cur.fetchone()
      Slave_IO_Running = row[10]
      Slave_SQL_Running = row[11]
      cur.close()

      if slave_cur.enable == False:
        if Slave_IO_Running == 'Yes' and Slave_SQL_Running == 'Yes':
          slave_cur.enable = True
        else:
          continue

      if Slave_IO_Running != 'Yes' or Slave_SQL_Running != 'Yes':
        atlas_setoffline(ip)
        slave_cur.enable = False
      else :
        atlas_setonline(ip)

  except Exception, e:
    logging.info('slave host[' + slave_cur.getHost() + ']die msg : ' + str(e))
    slave_cur.die = True
    atlas_setoffline(ip)

  time.sleep(int(auto_switch_sleep_time))
