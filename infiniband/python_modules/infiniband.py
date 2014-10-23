#/******************************************************************************
#* Portions Copyright (C) 2007 Novell, Inc. All rights reserved.
#*
#* Redistribution and use in source and binary forms, with or without
#* modification, are permitted provided that the following conditions are met:
#*
#*  - Redistributions of source code must retain the above copyright notice,
#*    this list of conditions and the following disclaimer.
#*
#*  - Redistributions in binary form must reproduce the above copyright notice,
#*    this list of conditions and the following disclaimer in the documentation
#*    and/or other materials provided with the distribution.
#*
#*  - Neither the name of Novell, Inc. nor the names of its
#*    contributors may be used to endorse or promote products derived from this
#*    software without specific prior written permission.
#*
#* THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS ``AS IS''
#* AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#* IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
#* ARE DISCLAIMED. IN NO EVENT SHALL Novell, Inc. OR THE CONTRIBUTORS
#* BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
#* CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
#* SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
#* INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
#* CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
#* ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
#* POSSIBILITY OF SUCH DAMAGE.
#*
#* Author: Brad Nicholes (bnicholes novell.com)
#******************************************************************************/

import logging
import os
import time
import subprocess

descriptions = {}
descriptors = []
last_update = 0
cur_time = 0
stats = {}
last_val = {}

MAX_UPDATE_TIME = 15

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s\t Thread-%(thread)d - %(message)s")
logging.debug('starting up')

PERFQUERY='/usr/sbin/perfquery'

def update_stats():
	logging.debug('updating stats')
	global descriptions, last_update, stats, last_val, cur_time
        global MAX_UPDATE_TIME

        cur_time = time.time()

        if cur_time - last_update < MAX_UPDATE_TIME:
                logging.debug(' wait ' + str(int(MAX_UPDATE_TIME - (cur_time - last_update))) + ' seconds')
                return True

        #####
        # Update stats
        stats = {}

	# Get data from perfquery
	p = subprocess.Popen([PERFQUERY],stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	out, err = p.communicate()

	for line in out.splitlines():
		#Parse output
		pass

	logging.debug(' success refreshing stats')
        logging.debug(' stats: ' + str(stats))
        logging.debug(' last_val: ' + str(stats))

        last_update = cur_time
        return True

def get_stat(name):
	logging.debug(' getting stat: ' + name)
	global stats

	ret = update_stats()

	if ret:
		fir = name.find('_')
                sec = name.find('_', fir + 1)

                label = name[sec + 1:]

		try:
			return int(stats[label])
		except:
                        logging.warning('failed to fetch ' + name)
                        return 0
        else:
                return 0

def metric_init(params):
        '''Initialize the module and return all metric descriptors'''
        global descriptions
        global descriptors

        descriptions = dict(
		rx_data={
			'units': 'bytes',
			'description': 'Bytes Received',},
		tx_data={
			'units': 'bytes',
                        'description': 'Bytes Sent',},
		rx_pkts={
			'units': 'packets',
			'description': 'Packets Received',},
		tx_pkts={
                        'units': 'packets',
                        'description': 'Packets Sent',},
		symbol_errs={
			'units': 'count',
			'description': 'Symbol Errors',},
		)

	update_stats()

	for label in descriptions:
		logging.debug(' Parsing description: ' + label)
		d = {
			'name': 'ib_' + label,
			'call_back': get_stat,
			'time_max': MAX_UPDATE_TIME,
			'value_type': 'uint',
			'units': descriptions[label]['units'],
			'slope': 'both',
			'format': '%u',
			'description': label,
			'groups': 'infiniband'
		}

		d.update(descriptions[label])
		descriptors.append(d)

        return descriptors

def metric_cleanup():
        '''Clean up the module
        Called on shutdown'''
        pass

if __name__ == '__main__':
	params = {}
	metric_init(params)
        while True:
                for d in descriptors:
                        v = d['call_back'](d['name'])
                        print 'value for %s is %u' % (d['name'], v)

                print 'Sleeping 15 seconds'
                time.sleep(15)

