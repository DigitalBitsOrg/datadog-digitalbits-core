import json
import requests
from checks import AgentCheck
from subprocess import check_output


class DigitalBitsCore(AgentCheck):


    def check(self, instance):
        metric_prefix = self.init_config.get('metric_prefix', 'digitalbits-core')
        network = self.init_config.get('network', 'livenet')

        dbc_stats = self.get_digitalbits_stats()
        self.gauge('%s.status' % metric_prefix, dbc_stats['state'], tags=['network:'+network])
        self.gauge('%s.peers' % metric_prefix, dbc_stats['peers'], tags=['network:'+network])
        self.gauge('%s.ledger' % metric_prefix, dbc_stats['ledger'], tags=['network:'+network])
        self.gauge('%s.protocol' % metric_prefix, dbc_stats['protocol'], tags=['network:'+network])
        self.gauge('%s.quorum_agree' % metric_prefix, dbc_stats['quorum_agree'], tags=['network:'+network])
        self.gauge('%s.quorum_disagree' % metric_prefix, dbc_stats['quorum_disagree'], tags=['network:'+network])
        self.gauge('%s.quorum_failed' % metric_prefix, dbc_stats['quorum_failed'], tags=['network:'+network])
        self.gauge('%s.quorum_missing' % metric_prefix, dbc_stats['quorum_missing'], tags=['network:'+network])
        self.gauge('%s.age' % metric_prefix, dbc_stats['age'], tags=['network:'+network])


    def get_digitalbits_stats(self):
        dbc_url = self.init_config.get('dbc_url', 'http://localhost:11626')

        try:
            response = requests.get(dbc_url + "/info")
            status = json.loads(response.text)

            quorum = list(status['info']['quorum'].values())[0]

            state = status['info']['state']
            
            if state == "Catching up":
                stateCode = 3

            elif state == "Synced!":
                stateCode = 5
                
            else:
                stateCode = 1
            
            

            return {
                        'state': stateCode,
                        'peers': status['info']['peers']['authenticated_count'],
                        'ledger': status['info']['ledger']['num'],
                        'protocol': status['info']['protocol_version'],
                        'quorum_agree': quorum['agree'],
                        'quorum_disagree': quorum['disagree'],
                        'quorum_failed': quorum['fail_at'],
                        'quorum_missing': quorum['missing'],
                        'age': status['info']['ledger']['age']
                    }


        except (requests.Timeout, requests.ConnectionError, KeyError) as e:
            return {
                'state': 0,
                'peers': 0,
                'ledger': 0,
                'protocol': 0,
                'quorum_agree': 0,
                'quorum_disagree': 0,
                'quorum_failed': 0,
                'quorum_missing': 0,
                'age': 0

            }
        


if __name__ == '__main__':
    check.check(instance)