
import re
from gobject import *
import telnet
from ICManager import ICManager

types = "(Blitz|Lightning|Standard)"
days = "(Mon|Tue|Wed|Thu|Fri|Sat|Sun)"
months = "(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"

AMOUNT_OF_NEWSITEMS = 5

class NewsManager (ICManager):
    
    __gsignals__ = {
        'readNews' : (SIGNAL_RUN_FIRST, TYPE_NONE, (object,)),
    }
    
    def __init__ (self):
        ICManager.__init__(self)
    
    def start (self):
        self.news = {}
        telnet.expect ("(\d+) \(%s, %s +(\d+)\) (.*?)\n" % (days, months), self.onNewsItem )
        print >> telnet.client, "news"
    
    def onNewsItem (self, client, groups):
        
        no, weekday, month, day, title = groups
        self.news[no] = [_(weekday), _(month), day, title, ""]
        
        if len(self.news) <= AMOUNT_OF_NEWSITEMS:
            # the "news" command, gives us the latest 10 news items from the
            # oldest to the newest.
            # We only want the 5 newest, so we skip the first 5 entries.
            return
        elif len(self.news) == 10:
            # No need to check the expression any more
            telnet.unexpect (self.onNewsItem)
        
        def callback (client, groups):
            telnet.unexpect(callback)
            details = groups[0].replace("\n\r\\   ", " ").replace("  ", " ")
            self.news[no][4] = details
            self.emit("readNews", self.news[no])
        
        telnet.expect ( "%s[\s\n]+(.+?)[\s\n]+Posted by" % re.escape(title), callback, re.DOTALL)
        print >> telnet.client, "news", no

nm = NewsManager()
