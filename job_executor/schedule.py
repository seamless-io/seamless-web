# TODO: implement scheduler

# def generate_logs(api_key: str, logstream: Iterable[bytes], timestamp_str: str):
#     cloud_watch = boto3.client('logs', region_name=os.getenv('AWS_REGION_NAME'))
#     log_group_name = f'/seamless/api_key/{api_key}'
#     try:
#         cloud_watch.create_log_group(
#             logGroupName=log_group_name
#         )
#         cloud_watch.put_retention_policy(
#             logGroupName=log_group_name,
#             retentionInDays=JOB_LOGS_RETENTION_DAYS
#         )
#     except ClientError as e:
#         if e.response['Error']['Code'] == 'ResourceAlreadyExistsException':
#             pass  # If log group already exists - it's fine
#         else:
#             raise e
#     cloud_watch.create_log_stream(
#         logGroupName=log_group_name,
#         logStreamName=timestamp_str
#     )

#     sequence_token = None
#     for line in logstream:
#         log_args = {
#             'logGroupName': log_group_name,
#             'logStreamName': timestamp_str,
#             'logEvents': [
#                 {
#                     'timestamp': int(round(time.time() * 1000)),
#                     'message': str(line, "utf-8")
#                 }
#             ],

#         }
#         if sequence_token:
#             log_args.update({
#                 'sequenceToken'
#                 : sequence_token
#             })
#         response = cloud_watch.put_log_events(**log_args)
#         sequence_token = response['nextSequenceToken']
#         yield line
