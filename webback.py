# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <mutzel@saeuferleber.de> wrote this file. As long as you retain this notice you
# can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return
# ----------------------------------------------------------------------------

from __future__ import with_statement 
import urllib2
import re
import sys

class MySqlDumper:

    url = 'http://localhost/mysqldumper/'
    user = 'admin'
    password = 'admin'    
    input_box_pattern = '<input type="hidden" name="(?P<name>.*?)" value="(?P<value>.*?)">'
    opener = None

    def __init__(self, url, user, password):
        self.url = url
        self.user = user
        self.password = password
        self.create_opener()

    def create_opener(self):
        pword_manager = urllib2.HTTPPasswordMgrWithDefaultRealm()
        pword_manager.add_password(None, self.url, self.user, self.password)
        self.opener = urllib2.build_opener(urllib2.HTTPBasicAuthHandler(pword_manager))
        
    def dump(self, status = lambda data: None, data = dict()):
        new_data = self.get_data_dictionary(self.opener.open("%s/dump.php" % self.url, self.get_data(data)).read())
        if(len(new_data) == 0):
            return data
        status(new_data)
        return self.dump(status, new_data);
        
    def download(self, data, filename):
        with open(filename, "wb") as file:
            file.write(self.opener.open("%swork/backup/%s" % (self.url, data['backupdatei'])).read())        

    def get_data_dictionary(self, html):
        return dict([(match)for match in re.findall(self.input_box_pattern,html)])

    def get_data(self, dictionary):
        return "&".join(["%s=%s" % (key, dictionary[key]) for key in dictionary])


def print_status(data):
    print "%s of %s" % (data['countdata'], data['totalrecords'])
        
def main(args=sys.argv):
    if len(args) <> 5:
        print "Too few argument were given. %d" % len(args)
        print "MySqlDumper.py <url> <user> <password> <download_file_name>"
        return
        
    dumper = MySqlDumper(args[1], args[2], args[3])
    dumper.download(dumper.dump(print_status), args[4])
    print "Done."

if __name__ == "__main__":
    main()


