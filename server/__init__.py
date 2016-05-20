from girder.api import access
from girder.api.describe import Description, describeRoute
from girder.api.rest import Resource, loadmodel, filtermodel
from girder.constants import AccessType
from girder.plugins.worker import utils


class DockerTest(Resource):
    def __init__(self):
        Resource.__init__(self)

        self.route('POST', ('outputs',), self.testOutputs)

    @access.user
    @filtermodel('job', 'jobs')
    @describeRoute(
        Description('Test docker outputs.')
    )
    def testOutputs(self, params):
        token = self.getCurrentToken()

        jobModel = self.model('job', 'jobs')

        job = jobModel.createJob(
            title='docker output stream test', type='docker_test',
            handler='worker_handler', user=self.getCurrentUser())
        jobToken = jobModel.createJobToken(job)

        kwargs = {
            'task': {
                'mode': 'docker',
                'docker_image': 'test/test:latest',
                'pull_image': False,
                'inputs': [],
                'outputs': [{
                    'id': 'my_named_pipe',
                    'target': 'filepath',
                    'format': 'text',
                    'stream': True,
                    'type': 'string'
                }]
            },
            'inputs': {},
            'outputs': {
                'my_named_pipe': {
                    'mode': 'http',
                    'url': 'http://localhost:8801',
                    'method': 'POST',
                    'format': 'text',
                    'type': 'string',
                }
            },
            'jobInfo': utils.jobInfoSpec(job, jobToken)
        }
        job['kwargs'] = kwargs
        job = jobModel.save(job)
        jobModel.scheduleJob(job)
        return job


def load(info):
    info['apiRoot'].docker_test = DockerTest()
