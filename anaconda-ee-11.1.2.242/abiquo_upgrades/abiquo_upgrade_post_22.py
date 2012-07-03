import os
import iutil
import shutil
import logging
import ConfigParser

log = logging.getLogger("anaconda")

def abiquo_upgrade_post(anaconda):

    schema_path = anaconda.rootPath + "/usr/share/doc/abiquo-server/database/kinton-latest-delta.sql"
    work_path = anaconda.rootPath + "/opt/abiquo/tomcat/work"
    temp_path = anaconda.rootPath + "/opt/abiquo/tomcat/temp"
    server_xml_path = anaconda.rootPath + "/opt/abiquo/tomcat/conf/Catalina/localhost/server.xml"
    
    # redis vars
    redis_port = 6379
    redis_sport = str(redis_port)

    # Clean tomcat 
    if os.path.exists(work_path):
        log.info("ABIQUO: Cleaning tomcat work folder...")
        iutil.execWithRedirect("/bin/rm",
                                ['-rf',work_path],
                                stdout="/dev/tty5", stderr="/dev/tty5",
                                root=anaconda.rootPath)
    if os.path.exists(temp_path):
        log.info("ABIQUO: Cleaning tomcat temp folder...")
        iutil.execWithRedirect("/bin/rm",
                                ['-rf',temp_path],
                                stdout="/dev/tty5", stderr="/dev/tty5",
                                root=anaconda.rootPath)
    
    # Remove deprecated server.xml
    if os.path.exists(server_xml_path):
        log.info("ABIQUO: Removing old server.xml file...")
        iutil.execWithRedirect("/bin/rm",
                                ['-rf',server_xml_path],
                                stdout="/dev/tty5", stderr="/dev/tty5",
                                root=anaconda.rootPath)
   
    # Upgrade database if this is a server install
    if os.path.exists(schema_path):
        schema = open(schema_path)
        log.info("ABIQUO: Updating Abiquo database (community delta)...")
        iutil.execWithRedirect("/sbin/ifconfig",
                                ['lo', 'up'],
                                stdout="/dev/tty5", stderr="/dev/tty5",
                                root=anaconda.rootPath)
        
        iutil.execWithRedirect("/etc/init.d/mysqld",
                                ['start'],
                                stdout="/mnt/sysimage/var/log/abiquo-postinst.log", stderr="//mnt/sysimage/var/log/abiquo-postinst.log",
                                root=anaconda.rootPath)

        iutil.execWithRedirect("/usr/bin/mysql",
                                ['kinton'],
                                stdin=schema,
                                stdout="/mnt/sysimage/var/log/abiquo-postinst.log", stderr="//mnt/sysimage/var/log/abiquo-postinst.log",
                                root=anaconda.rootPath)
        schema.close()
        


    # Redis patch on server
    if os.path.exists(schema_path):
        log.info("ABIQUO: Applying redis patch...")
        iutil.execWithRedirect("/usr/bin/redis-cli",
                                ['-h', 'localhost', '-p', redis_sport ,"PING"],
                                stdout="/mnt/sysimage/var/log/abiquo-postinst.log", stderr="//mnt/sysimage/var/log/abiquo-postinst.log",
                                root=anaconda.rootPath)      

        cmd = iutil.execWithRedirect("/usr/bin/redis-cli",
                                ['-h', 'localhost', '-p', redis_sport ,'keys','Owner:*:*'],
                                stdout="/mnt/sysimage/var/log/abiquo-postinst.log", stderr="//mnt/sysimage/var/log/abiquo-postinst.log",
                                root=anaconda.rootPath)


        for owner in cmd.stdout:
            owner = owner.strip()
            key = owner[:owner.rfind(":")]
            iutil.execWithRedirect("/usr/bin/redis-cli",
                                ['-h', 'localhost', '-p', redis_sport ,'sadd',key,owner],
                                stdout="/mnt/sysimage/var/log/abiquo-postinst.log", stderr="//mnt/sysimage/var/log/abiquo-postinst.log",
                                root=anaconda.rootPath)
            log.info("ABIQUO: "+owner+" indexed.")


    # Add new 2.2 properties
    sys_props = anaconda.rootPath + '/opt/abiquo/config/abiquo.properties'
    if os.path.exists(sys_props):
        log.info('ABIQUO: Updating system properties')
        try:
            config = ConfigParser.ConfigParser()
            config.optionxform = str
            config.read(sys_props)
            if config.has_section('server'):
                    if not config.has_option('server', 'abiquo.api.networking.nicspervm'):
                            config.set('server', 'abiquo.api.networking.nicspervm', '0')
                    if not config.has_option('server', 'abiquo.api.networking.allowMultipleNicsVlan'):
                            config.set('server', 'abiquo.api.networking.allowMultipleNicsVlan', 'True')

    # restore fstab
    backup_dir = anaconda.rootPath + '/opt/abiquo/backup/2.0'
    if os.path.exists('%s/fstab.anaconda' % backup_dir):
        shutil.copyfile("%s/fstab.anaconda" % backup_dir,
                '%s/etc/fstab' % anaconda.rootPath)


