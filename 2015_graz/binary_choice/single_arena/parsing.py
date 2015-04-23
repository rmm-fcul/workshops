import yaml
import os


#{{{ find_comm_links -- maybe should be in utils or parsing lib?
def find_comm_links(casu_names, rtc_path, suffix="-sim", verb=False):
    nodes = []
    edges = []

    # for each rtc file, find the nodes specified, and any communication links
    for name in casu_names:
        fname = "{}{}.rtc".format(name, suffix)
        rtc = os.path.join(rtc_path, fname)
        if verb: print "[I] considering casu {} \n\t('{}')".format(name, rtc)
        # should handle the possibility of file missing!
        try:
            deploy = yaml.safe_load(file(rtc, 'r'))
            # verify that the deployment file is for the same named object
            if not name == deploy['name']:
                print "[W] CASU RTC file mismatching this casu, skipping", name, deploy['name']
                continue
            nodes.append(name)
            if 'neighbors' in deploy and deploy['neighbors'] is not None:
                for k, v in deploy['neighbors'].iteritems():
                    n = v.get('name', None)
                    if verb > 1: print v, n
                    if n:
                        edges.append((name, n))
        except IOError:
            print "[W] could not read rtc conf file for casu {}".format(name)


    return nodes, edges
#}}}
#{{{ find_comm_link_mapping
def find_comm_link_mapping(casu_name, rtc_path, suffix="-sim", verb=False):
    '''
    find all links in rtc file, and return in a mapping from physical target
    to logical name (when receiving messages, the physical name is provided but
    the CASU behaviour is typically defined in terms of logical names).

    :param str casu_name: name of the CASU to inspect
    :param str rtc_path:  the directory containing rtc files
    :param str suffix:    suffix for RTC convention (e.g. -sim or -physical)
    :param bool verb:     verbose output switch
    :return:              dict of physical:logical names

    '''

    phys_logi_map = {}

    fname = "{}{}.rtc".format(casu_name, suffix)
    rtc = os.path.join(rtc_path, fname)
    if verb: print "[I] considering casu {} \n\t('{}')".format(casu_name, rtc)
    # should handle the possibility of file missing!
    try:
        deploy = yaml.safe_load(file(rtc, 'r'))
        # verify that the deployment file is for the same named object
        if not casu_name == deploy['name']:
            print "[W] CASU RTC file mismatching this casu, skipping", casu_name, deploy['name']

        elif 'neighbors' in deploy and deploy['neighbors'] is not None:
            for k, v in deploy['neighbors'].iteritems():
                neigh = v.get('name', None)
                if verb > 1: print v, neigh
                if neigh:
                    phys_logi_map[neigh] = k

    except IOError:
        print "[W] could not read rtc conf file for casu {}".format(casu_name)


    return phys_logi_map
#}}}
