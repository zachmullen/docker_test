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
    @loadmodel(map={'folderId': 'folder'}, model='folder', level=AccessType.WRITE)
    @loadmodel(map={'itemId': 'item'}, model='item', level=AccessType.READ)
    @filtermodel('job', 'jobs')
    @describeRoute(
        Description('Test docker outputs.')
        .param('folderId', 'Where to write container outputs.')
        .param('itemId', 'The input file.')
    )
    def testOutputs(self, folder, item, params):
        token = self.getCurrentToken()

        jobModel = self.model('job', 'jobs')

        job = jobModel.createJob(
            title='docker output test: %s' % folder['name'], type='docker_test',
            handler='worker_handler', user=self.getCurrentUser())
        jobToken = jobModel.createJobToken(job)

        kwargs = {
            'task': {
                'mode': 'docker',
                'docker_image': 'testoutputs:latest',
                'pull_image': False,
                'inputs': [{
                    'id': 'input',
                    'target': 'filepath',
                    'format': 'text',
                    'type': 'string'
                }],
                'outputs': [{
                    'id': 'out.txt',
                    'target': 'filepath',
                    'format': 'text',
                    'type': 'string'
                }]
            },
            'inputs': {
                'input': utils.girderInputSpec(
                    item, resourceType='item', token=token)
            },
            'outputs': {
                'out.txt': utils.girderOutputSpec(
                    folder, token)
            },
            'jobInfo': utils.jobInfoSpec(job, jobToken)
        }
        job['kwargs'] = kwargs
        job = jobModel.save(job)
        jobModel.scheduleJob(job)
        return job


def load(info):
    info['apiRoot'].docker_test = DockerTest()
