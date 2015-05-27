# coding=utf-8

"""
Collect XEN master stats from xentop

#### Dependencies

sudoers access required:
    diamond      ALL         = (root)     NOPASSWD: /usr/sbin/xentop

#### Config example
    [[XenTopCollector]]
    enabled = True
    xentop_metrics = 'CPU(sec) MEM(k) NETTX(k) NETRX(k) VBD_RD VBD_WR'

#### Full list of metrics available
    NAME  STATE   CPU(sec) CPU(%)     MEM(k) MEM(%)  MAXMEM(k) MAXMEM(%) VCPUS NETS NETTX(k) NETRX(k) VBDS   VBD_OO   VBD_RD   VBD_WR  VBD_RSECT  VBD_WSECT SSID
"""

from diamond import collector
import subprocess

class XenTopCollector(collector.Collector):

    def __init__(self, config, handlers):
        collector.Collector.__init__(self, config, handlers)

    def get_default_config_help(self):
        config_help = super(XenTopCollector, self).get_default_config_help()
        config_help.update({})
        return config_help

    def get_default_config(self):
        config = super(XenTopCollector, self).get_default_config()
        config.update({
            'enabled':  'True',
            'path':     'xentop',
            'xentop_metrics': 'CPU(sec) MEM(k) NETTX(k) NETRX(k) VBD_RD VBD_WR'
        })
        return config

    @staticmethod
    def poll():
        try:
            output = subprocess.Popen(['/usr/bin/sudo', '/usr/sbin/xentop', '-b', '-i1', '-f'],
                    stdout=subprocess.PIPE).communicate()[0].splitlines()

        except OSError:
            output = []

        return output

    def collect(self):
        output = self.poll()
        metrics = self.config['xentop_metrics'].split()

        if len(output) < 2:
            return None

        i = 0
        fields = {}
        for field in output[0].split():
            fields[field] = i
            i = i + 1


        for line in output[2:]:
            values = line.split()
            if len(values) < i:
                continue

            name = values[fields['NAME']].split('.')[0].lower()
            for metric in metrics:
                self.publish("%s.%s" % (name, self.mangle(metric)), values[fields[metric]])

    @staticmethod
    def mangle(string):
        return string.replace('%','pct').replace('(','_').replace(')','')


