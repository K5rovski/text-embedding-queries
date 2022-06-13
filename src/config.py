keys = '''streams/dev
firehose/dev
kinesisanalytics/dev
athena/ug
redshift/mgmt
redshift/dg
redshift/gsg
quicksight/user
quicksight/developerguide
glue/ug
glue/dg
emr/ManagementGuide
emr/ReleaseGuide
dms/sbs
dms/userguide
AWSSimpleQueueService/SQSDeveloperGuide
kms/developerguide
opensearch-service/developerguide
datapipeline/DeveloperGuide
AmazonElastiCache/red-ug
AmazonElastiCache/mem-ug
directconnect/UserGuide
sagemaker/dg
singlesignon/userguide
singlesignon/developerguide
datasync/userguide
sns/dg
step-functions/dg
snowball/developer-guide
snowball/ug
msk/developerguide
lake-formation/dg
neptune/userguide
documentdb/developerguide
timestream/developerguide
macie/user
amazondynamodb/developerguide
AmazonS3/userguide
amazonglacier/dev
lambda/dg
amazon-mq/developer-guide
amazon-mq/migration-guide'''.splitlines()


serviceD=dict(streams='streams',
              firehose='firehose',
              kinesisanalytics='analytics',
              athena='athena',
              redshift='redshift',
              quicksight='quicksight',
              glue='glue',
              emr='emr',
              dms='dms',
              kms='kms',
              AmazonS3='s3',
              datapipeline='datapipeline',
              elasticache='elasticache',
              directconnect='directconnect',
              sagemaker='sagemaker',
              sns='sns',
              snowball='snowball',
              amazondynamodb='dynamodb',
              AWSSimpleQueueService='sqs',
              AmazonElastiCache='elasticache',
              singlesignon='singlesignon',
              datasync='datasync',
              macie='macie',
              neptune='neptune',
              timestream='timestream',
              documentdb='documentdb',
              msk='kafka',
              amazonglacier='glacier',
             )

serviceD = {**{'opensearch-service':'opensearch',
              'step-functions':'stepfunctions',
              'lake-formation':'lakeformation',
              'amazon-mq':'mq',
              'lambda':'lambda'},**serviceD}

guideD = dict(dg='developer',
             user='user',
              ug='user',
             dev='developer',
             mgmt='management',
             gsg='getting-started',
             ManagementGuide='management',
             ReleaseGuide='release',
             sbs='step-by-step',
             developerguide='developer',
             DeveloperGuide='developer',
             SQSDeveloperGuide='developer',
              UserGuide='user',
              userguide='user',
              operatorguide='operator'
             )
guideD = {**{'red-ug':'redis','mem-ug':'memcache',
            'developer-guide':'developer',
            'migration-guide':'migration'}, **guideD}