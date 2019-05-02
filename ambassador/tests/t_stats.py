from kat.harness import Query

from abstract_tests import DEV, AmbassadorTest, HTTP


class StatsdTest(AmbassadorTest):
    skip_in_dev = True

    envs = {
        'STATSD_ENABLED': 'true',
        'STATSD_HOST': 'statsd'
    }

    configs = {
        'target': '''
---
apiVersion: ambassador/v1
kind:  Mapping
name:  {self.name}
prefix: /{self.name}/
service: http://{self.target.path.fqdn}
---
apiVersion: ambassador/v1
kind:  Mapping
name:  {self.name}-reset
case_sensitive: false
prefix: /reset/
rewrite: /RESET/
service: statsd
'''
    }

    extra_pods = {
        'statsd': {
            'image': 'dwflynn/stats-test:0.1.0',
            'envs': {
                'STATSD_TEST_CLUSTER': "cluster_http___statsdtest_http",
                # 'STATSD_TEST_DEBUG': 'true'
            },
            'ports': [
                ( 'tcp', 80, 3000 ),
                ( 'udp', 8125, 8125 )
            ]
        }
    }

    # extra_pods = {
    #     'statsd': {
    #         'pod': {
    #             'image': 'dwflynn/stats-test:0.1.0',
    #             'ports': [
    #                 {
    #                     'name': 'statsd-api',
    #                     'containerPort': 8125,
    #                     'protocol': 'UDP'
    #                 },
    #                 {
    #                     'name': 'statsd-www',
    #                     'containerPort': 3000,
    #                     'protocol': 'TCP'
    #                 }
    #             ],
    #             'envs': {
    #                 'STATSD_TEST_CLUSTER': "cluster_http___statsdtest_http",
    #                 # 'STATSD_TEST_DEBUG': 'true'
    #             }
    #         },
    #         'ports': [
    #             {
    #                 'port': 8125,
    #                 'name': 'statsd-api',
    #                 'targetPort': 'statsd-api',
    #                 'protocol': 'UDP',
    #             },
    #             {
    #                 'port': 80,
    #                 'name': 'statsd-www',
    #                 'targetPort': 'statsd-www',
    #                 'protocol': 'TCP',
    #             }
    #         ]
    #     }
    # }

    def init(self):
        self.target = HTTP()

    def requirements(self):
        yield ("url", Query("http://statsd/RESET/"))
        yield ("url", Query(self.url("RESET/")))

    def queries(self):
        for i in range(1000):
            yield Query(self.url(self.name + "/"), phase=1)

        yield Query("http://statsd/DUMP/", phase=2)

    def check(self):
        stats = self.results[-1].json or {}

        cluster_stats = stats.get('cluster_http___statsdtest_http', {})
        rq_total = cluster_stats.get('upstream_rq_total', -1)
        rq_200 = cluster_stats.get('upstream_rq_200', -1)

        assert rq_total == 1000, f'expected 1000 total calls, got {rq_total}'
        assert rq_200 > 990, f'expected 1000 successful calls, got {rq_200}'


class DogstatsdTest(AmbassadorTest):
    skip_in_dev = True

    envs = {
        'STATSD_ENABLED': 'true',
        'STATSD_HOST': 'statsd',
        'DOGSTATSD': 'true'
    }

    configs = {
        'target': '''
---
apiVersion: ambassador/v1
kind:  Mapping
name:  {self.name}
prefix: /{self.name}/
service: http://{self.target.path.fqdn}
---
apiVersion: ambassador/v1
kind:  Mapping
name:  {self.name}-reset
case_sensitive: false
prefix: /reset/
rewrite: /RESET/
service: statsd
'''
    }

    extra_pods = {
        'statsd': {
            'image': 'dwflynn/stats-test:0.1.0',
            'envs': {
                'STATSD_TEST_CLUSTER': "cluster_http___dogstatsdtest_http"
            },
            'ports': [
                ( 'tcp', 80, 3000 ),
                ( 'udp', 8125, 8125 )
            ]
        }
    }

    # extra_pods = {
    #     'statsd': {
    #         'pod': {
    #             'image': 'dwflynn/stats-test:0.1.0',
    #             'ports': [
    #                 {
    #                     'name': 'statsd-api',
    #                     'containerPort': 8125,
    #                     'protocol': 'UDP'
    #                 },
    #                 {
    #                     'name': 'statsd-www',
    #                     'containerPort': 3000,
    #                     'protocol': 'TCP'
    #                 }
    #             ],
    #             'envs': {
    #                 'STATSD_TEST_CLUSTER': "cluster_http___dogstatsdtest_http",
    #                 # 'STATSD_TEST_DEBUG': 'true'
    #             }
    #         },
    #         'ports': [
    #             {
    #                 'port': 8125,
    #                 'name': 'statsd-api',
    #                 'targetPort': 'statsd-api',
    #                 'protocol': 'UDP',
    #             },
    #             {
    #                 'port': 80,
    #                 'name': 'statsd-www',
    #                 'targetPort': 'statsd-www',
    #                 'protocol': 'TCP',
    #             }
    #         ]
    #     }
    # }

    def init(self):
        self.target = HTTP()

    def requirements(self):
        yield ("url", Query("http://statsd/RESET/"))
        yield ("url", Query(self.url("RESET/")))

    def queries(self):
        for i in range(1000):
            yield Query(self.url(self.name + "/"), phase=1)

        yield Query("http://statsd/DUMP/", phase=2)

    def check(self):
        stats = self.results[-1].json or {}

        cluster_stats = stats.get('cluster_http___dogstatsdtest_http', {})
        rq_total = cluster_stats.get('upstream_rq_total', -1)
        rq_200 = cluster_stats.get('upstream_rq_200', -1)

        assert rq_total == 1000, f'expected 1000 total calls, got {rq_total}'
        assert rq_200 > 990, f'expected 1000 successful calls, got {rq_200}'
