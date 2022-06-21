

model_path = "/Users/kiks/Downloads/uni-encoder-2/"

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
amazon-mq/migration-guide
AWSEC2/UserGuide
AmazonRDS/UserGuide
AmazonRDS/AuroraUserGuide
secretsmanager/userguide
cloudhsm/userguide
IAM/UserGuide'''.splitlines()

url_checks = dict(
    check_ebs=lambda url: True if (('ebs' in url.lower() and 'AWSEC2' in url) or 'AWSEC2' not in url) else False
)

url_start = {
    'https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/concepts.html': 'https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/Storage.html'
}

serviceD = dict(streams='streams',
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
                AWSEC2='ebs',
                AmazonRDS='rds',
                secretsmanager='secretsmanager',
                cloudhsm='cloudhsm',
                IAM='iam',

                )

serviceD = {**{'opensearch-service': 'opensearch',
               'step-functions': 'stepfunctions',
               'lake-formation': 'lakeformation',
               'amazon-mq': 'mq',
               'lambda': 'lambda'}, **serviceD}

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
              operatorguide='operator',
              AuroraUserGuide='aurora-user'
              )
guideD = {**{'red-ug': 'redis', 'mem-ug': 'memcache',
             'developer-guide': 'developer',
             'migration-guide': 'migration'}, **guideD}

all_aws_services = [
    "firehose|streams|analytics|sqs|sns|mq|dms|" \
    "directconnect|kafka|snowball|datapipeline|datasync|lambda",
    "s3|dynamodb|glacier|documentdb|elasticache|neptune|rds|redshift|timestream",
    "glue|emr|lambda|lakeformation|stepfunctions|datapipeline|sagemaker",
    "athena|elasticsearch|"
    "redshift|analytics|quicksight|emr|glue",
    'kms|singlesignon|macie|secretsmanager|cloudhsm|iam'
]
aws_categories = ['collection', 'storage',
                  'processing', 'analyze',
                  'security']

all_queries = ['''data loss within limits| failure protection|loss limits| failure limits|  Evaluate that the data loss is within tolerance limits in the event of failures
costs with transfer from source to aws| cost for data transfer|networking, bandwidth, ETL/data migration costs for collection| Evaluate costs associated with data acquisition, transfer, and provisioning from various sources into the collection system (e.g., networking, bandwidth, ETL/data migration costs)
failure scenario, which remediation can be had|impact of failure of data collection| Assess the failure scenarios that the collection system may undergo, and take remediation actions based on impact
data persistence| data persistence while transferring|data  Determine data persistence at various points of data capture
latency of data collection, data transfer system|arrival time of data collection| Identify the latency characteristics of the collection system
volume and flow of incoming data|streaming data vs transactional data vs batch data, flow and volume| Describe and characterize the volume and flow characteristics of incoming data (streaming, transactional, batch)
data flow characteristics|flow specifications of data| Match flow characteristics of data to potential solutions
scalability cost fault tolerance of data ingestions| Assess the tradeoffs between various ingestion services taking into account scalability, cost, fault tolerance, latency, etc.
throughput of data ingestion,collection services| throughput and bottlenecks of data ingestion| Explain the throughput capability of a variety of different types of data collection and identify bottlenecks
ways to connect sources of data collection, ingestion|list of sources connections for data ingestion| Choose a collection solution that satisfies connectivity constraints of the source data system

source data changes| source data migrations|  Describe how to capture data changes at the source
data structure format and compression and encryption possibilities| Discuss data structure and format, compression applied, and encryption requirements
out of order data delivery|duplicate data|'at most once', 'at least once', 'exactly once'| Distinguish the impact of out-of-order delivery of data, duplicate delivery of data, and the tradeoffs between at-most-once, exactly-once, and at-least-once processing
transform and filter data while ingesting|filter transform data in collecting| Describe how to transform and filter data during the collection process



''',
               '''
               cost, performance of data storage|cost performance breakdown| Determine the appropriate storage service(s) on the basis of cost vs. performance
           durability reliability latency of data storage| Understand the durability, reliability, and latency characteristics of the storage solution based on requirements
           strong, eventual consistency| Determine the requirements of a system for strong vs. eventual consistency of the storage system
           data freshness|'fresh data'| Determine the appropriate storage solution to address data freshness requirements

           update patterns for data|update patterns for storage|data update in storage system| Determine the appropriate storage solution based on update patterns (e.g., bulk, transactional, micro batching)
           access patterns for data|access patterns for storage|data access in storage system| Determine the appropriate storage solution based on access patterns (e.g., sequential vs. random access, continuous usage vs.ad hoc)
           append data vs update data|change characteristics of data|data appending and data updating| Determine the appropriate storage solution to address change characteristics of data (appendonly changes vs. updates)
           long term storage vs transient storage|long term and short term data| Determine the appropriate storage solution for long-term storage vs. transient storage
           structured and semi-structured data|appropriate for semi structured data , structured data| Determine the appropriate storage solution for structured vs. semi-structured data
           query latency in storage|time of query in data storage| Determine the appropriate storage solution to address query latency requirements

           schema evolution in data storage|schema changes in data| Determine appropriate mechanisms to address schema evolution requirements
           list of storage formats| Select the storage format for the task
           compression, encoding in a data storage| Select the compression/encoding strategies for the chosen storage format
           data sorting and distribution in storage, for fast access|storage layout needed for efficient access| Select the data sorting and distribution strategies and the storage layout for efficient data access
           cost and performance implications for data distributions layouts and formats| Explain the cost and performance implications of different data distributions, layouts, and formats (e.g., size and number of files)
           data format and partitioning for optimized analysis| Implement data formatting and partitioning schemes for data-optimized analysis

           data lifecycle requirements| Determine the strategy to address data lifecycle requirements
           lifecycle and data retention policy| Apply the lifecycle and data retention policies to different storage solutions

           discovery of data sources| Evaluate mechanisms for discovery of new and updated data sources
           managing data catalogs|managing metadata of data| Evaluate mechanisms for creating and updating data catalogs and metadata
           search and retrieve data catalog|search and retrieve metadata| Explain mechanisms for searching and retrieving data catalogs and metadata
           tag and classify data| Explain mechanisms for tagging and classifying data

               ''',
               '''
               data preparation|usage requirements| Understand data preparation and usage requirements
           data source, data targets| Understand different types of data sources and targets
           performance for data orchestration| Evaluate performance and orchestration needs
           cost scalability availability of service| Evaluate appropriate services for cost, scalability, and availability

           extract load transform, ETL ELT for batch real time processing workload| Apply appropriate ETL/ELT techniques for batch and real-time workloads
           fail-over scaling replication mechanism options| Implement fail-over, scaling, and replication mechanisms
           concurrency techniques for processing| Implement techniques to address concurrency needs
           cost optimization efficiencies options| Implement techniques to improve cost-optimization efficiencies
           orchestration workflows|orchestration implementation| Apply orchestration workflows
           aggegated and enriched,combined data for downstream consumers| Aggregate and enrich data for downstream consumption

           automated workflow for repeatable processing| Implement automated techniques for repeatable workflows
           recovering and identifying processing failures| Apply methods to identify and recover from processing failures
           logging and monitoring for auditing and traceability| Deploy logging and monitoring solutions to enable auditing and traceability    
               ''',
               '''
               costs of analysis|costs of visualization| Determine costs associated with analysis and visualization
           scalability of analysis| Determine scalability associated with analysis
           failover recovery and fault tolerance within the RPO/RTO| Determine failover recovery and fault tolerance within the RPO/RTO
           availability characteristics of an analysis tool| Determine the availability characteristics of an analysis tool
           dynamic, interactive, and static data presentations| Evaluate dynamic, interactive, and static presentations of data
           performance requirements for visualization approach|pre-compute and consume static data vs. consume dynamic data| Translate performance requirements to an appropriate visualization approach (pre-compute and consume static data vs. consume dynamic data)

           comparison of analysis solutions| Evaluate and compare analysis solutions
           (streaming, interactive, collaborative, operational) data analysis| Select the right type of analysis based on the customer use case (streaming, interactive, collaborative, operational)

           metrics, KPIs, tabular, API output| Evaluate output capabilities for a given analysis solution (metrics, KPIs, tabular, API)
           data delivery web, mobile, email, collaborative notebooks etc...| Choose the appropriate method for data delivery (e.g., web, mobile, email, collaborative notebooks)
           data refresh schedule| Choose and define the appropriate data refresh schedule
           data freshness requirements elasticsearch quicksight emr notebooks| Choose appropriate tools for different data freshness requirements (e.g., Amazon Elasticsearch Service vs. Amazon QuickSight vs. Amazon EMR notebooks)
           visualization tools for interactive use cases, drill down, drill through, pivot| Understand the capabilities of visualization tools for interactive use cases (e.g., drill down, drill through and pivot)
           data acess mechanism|data access in memory vs direct access| Implement the appropriate data access mechanism (e.g., in memory vs. direct access)
           integrate multiple heterogeneous data sources| Implement an integrated solution from multiple heterogeneous data sources

           ''',
               '''
               authentication methods|authentication federated access SSO,IAM| Implement appropriate authentication methods (e.g., federated access, SSO, IAM)
               authorization methods|authorization policies ACL table,column level permissions| Implement appropriate authorization methods (e.g., policies, ACL, table/column level permissions)
               access control mechanism|access control security groups, iam role based access| Implement appropriate access control mechanisms (e.g., security groups, role-based control)

               data encryption, data masking need| Determine data encryption and masking needs
               data encryption approaches principle|comparison of server side encryption, client side encryption kms, cloudhsm| Apply different encryption approaches (server-side encryption, client-side encryption, AWS KMS, AWS CloudHSM)
               at rest, in transit encryption mechanism| Implement at-rest and in-transit encryption mechanisms
               data obfuscation and data masking techniques| Implement data obfuscation and masking techniques
               principle of key rotation, secrets management| Apply basic principles of key rotation and secrets management

               data governance and compliance requirements| Determine data governance and compliance requirements
               access and audit logging across data analytics services| Understand and configure access and audit logging across data analytics services
               appropriate controls to meet compliance requirements| Implement appropriate controls to meet compliance requirements
               '''
               ]