from swift.common.utils import get_logger, plugin_enabled
from swift import plugins
from ConfigParser import ConfigParser

class Gluster_plugin(object):
    """
    Update the environment with keys that reflect Gluster_plugin enabled
    """

    def __init__(self, app, conf):
        self.app = app
        self.conf = conf
        self.fs_name = 'Glusterfs'
        self.logger = get_logger(conf, log_route='gluster')

    def __call__(self, env, start_response):
        if not plugin_enabled():
            return self.app(env, start_response)
        env['Gluster_enabled'] =True
        fs_object = getattr(plugins, self.fs_name, False)
        if not fs_object:
            raise Exception('%s plugin not found', self.fs_name)

        env['fs_object'] = fs_object()
        fs_conf = ConfigParser()
        if fs_conf.read('/etc/swift/fs.conf'):
            try:
                env['root'] = fs_conf.get ('DEFAULT', 'mount_path')
            except NoSectionError, NoOptionError:
                self.logger.exception(_('ERROR mount_path not present'))
        return self.app(env, start_response)

def filter_factory(global_conf, **local_conf):
    """Returns a WSGI filter app for use with paste.deploy."""
    conf = global_conf.copy()
    conf.update(local_conf)

    def gluster_filter(app):
        return Gluster_plugin(app, conf)
    return gluster_filter
