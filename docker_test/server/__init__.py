import datetime

from girder.api import access
from girder.api.describe import Description, describeRoute
from girder.api.rest import Resource, loadmodel, filtermodel, iterBody, getApiUrl
from girder.constants import AccessType
from girder.models.notification import ProgressState
from girder.plugins.worker import utils


class DockerTest(Resource):
    def __init__(self):
        Resource.__init__(self)

        #self.route('POST', ('outputs',), self.testOutputs)
        self.route('POST', ('stream',), self.testStream)
        self.route('POST', ('stream_callback',), self.streamUpload)
        self.route('POST', ('fetch_parent',), self.testFetchParent)

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

    @access.user
    @loadmodel(map={'itemId': 'item'}, model='item', level=AccessType.READ)
    @filtermodel('job', 'jobs')
    @describeRoute(
        Description('Test docker streaming IO.')
        .param('itemId', 'The ID of the item to stream. CSV file works best.')
    )
    def testStream(self, item, params):
        token = self.getCurrentToken()

        jobModel = self.model('job', 'jobs')

        job = jobModel.createJob(
            title='docker stream test', type='docker_test',
            handler='worker_handler', user=self.getCurrentUser())
        jobToken = jobModel.createJobToken(job)
        apiUrl = getApiUrl()

        kwargs = {
            'task': {
                'mode': 'docker',
                'docker_image': 'testoutputs:latest',
                'pull_image': False,
                'inputs': [{
                    'id': 'input_pipe',
                    'target': 'filepath',
                    'stream': True
                }],
                'outputs': [{
                    'id': 'output_pipe',
                    'target': 'filepath',
                    'stream': True
                }]
            },
            'inputs': {
                'input_pipe': {
                    'mode': 'http',
                    'method': 'GET',
                    'url': '%s/item/%s/download' % (apiUrl, str(item['_id'])),
                    'headers': {
                        'Girder-Token': str(token['_id'])
                    }
                }
            },
            'outputs': {
                'output_pipe': {
                    'mode': 'http',
                    'method': 'POST',
                    'url': apiUrl + '/docker_test/stream_callback',
                    'headers': {
                        'Girder-Token': str(token['_id'])
                    }
                }
            },
            'validate': False,
            'auto_convert': False,
            'cleanup': False,
            'jobInfo': utils.jobInfoSpec(job, jobToken)
        }
        job['kwargs'] = kwargs
        job = jobModel.save(job)
        jobModel.scheduleJob(job)
        return job

    @access.user
    @describeRoute(None)
    def streamUpload(self, params):
        nmodel = self.model('notification')
        note = nmodel.initProgress(self.getCurrentUser(), 'Docker stream demo')
        for i, chunk in enumerate(iterBody(), 1):
            nmodel.updateProgress(note, message='%d: %s' % (i, chunk))

        nmodel.updateProgress(
            note, state=ProgressState.SUCCESS,
            expires=datetime.datetime.utcnow() + datetime.timedelta(seconds=10))

    @access.user
    @loadmodel(map={'fileId': 'file'}, model='file', level=AccessType.READ)
    @filtermodel('job', 'jobs')
    @describeRoute(
        Description('Test fetching of parent item.')
        .param('fileId', 'The ID of the file.')
    )
    def testFetchParent(self, file, params):
        token = self.getCurrentToken()

        jobModel = self.model('job', 'jobs')

        job = jobModel.createJob(
            title='Parent fetch test', type='parent_fetch_test',
            handler='worker_handler', user=self.getCurrentUser())
        jobToken = jobModel.createJobToken(job)

        kwargs = {
            'task': {
                'mode': 'python',
                'script': 'print(fp)\n',
                'inputs': [{
                    'id': 'fp',
                    'target': 'filepath',
                    'format': 'text',
                    'type': 'string'
                }],
                'outputs': []
            },
            'inputs': {
                'fp': utils.girderInputSpec(file, token=token, fetchParent=True)
            },
            'outputs': {},
            'validate': False,
            'auto_convert': False,
            'cleanup': False,
            'jobInfo': utils.jobInfoSpec(job, jobToken)
        }
        job['kwargs'] = kwargs
        job = jobModel.save(job)
        jobModel.scheduleJob(job)
        return job

def load(info):
    info['apiRoot'].docker_test = DockerTest()
