import os
import select
import time
import dotenv
import multiprocessing
import subprocess
import json
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.dnspod.v20210323 import dnspod_client, models


dotenv.load_dotenv(dotenv.find_dotenv())
SECRET_ID = os.environ['SECRET_ID']
SECRET_KEY = os.environ['SECRET_KEY']
RECORD_ID = os.environ['RECORD_ID']
DOMAIN_NAME = os.environ['DOMAIN_NAME']


def set_challenge(txt):
    try:
        cred = credential.Credential(SECRET_ID, SECRET_KEY)
        # 实例化一个http选项，可选的，没有特殊需求可以跳过
        httpProfile = HttpProfile()
        httpProfile.endpoint = "dnspod.tencentcloudapi.com"

        # 实例化一个client选项，可选的，没有特殊需求可以跳过
        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        # 实例化要请求产品的client对象,clientProfile是可选的
        client = dnspod_client.DnspodClient(cred, "", clientProfile)

        # 实例化一个请求对象,每个接口都会对应一个request对象
        req = models.ModifyRecordRequest()
        params = {
            "Domain": DOMAIN_NAME,
            "RecordType": "TXT",
            "RecordLine": "默认",
            "Value": txt,
            "RecordId": int(RECORD_ID),
            "SubDomain": "_acme-challenge"
        }
        req.from_json_string(json.dumps(params))

        # 返回的resp是一个ModifyRecordResponse的实例，与请求对象对应
        resp = client.ModifyRecord(req)
    except TencentCloudSDKException as err:
        raise err



def certbot():
    # Run the command
    process = subprocess.Popen(
        ["certbot", "certonly", "--manual"], 
        stdin=subprocess.PIPE, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE,
        text=True,
    )

    stage = 'init'
    outputs = ''

    input_queue = []

    while True:
        if len(input_queue):
            # Get the input from the queue and send it to the process' stdin
            input_text = input_queue.pop()
            process.stdin.write(input_text + '\n')
            process.stdin.flush()  # Make sure the input is sent immediately
            print(f"Sent to process: {input_text}")

        output_line = process.stdout.readline()

        # Put the output into the queue
        print(f"Output: {output_line.strip()}")
        # output_queue.put(output_line.strip())
        outputs += output_line

        # error_line = process.stderr.readline()
        # if error_line:
        #     print(f"Error: {error_line.strip()}")

        output = outputs
        if stage == 'init':
            if 'Please enter the domain' in output:
                print('INPUT DOMAIN')
                stage = 'domain'
                input_queue.append('*.' + DOMAIN_NAME)
            else:
                continue
        elif stage == 'domain':
            if (
                'Please deploy a DNS TXT record under the name' in output
                and 'Before continuing, verify the TXT record' in output
            ):
                output = output[output.index('with the following value:') + 25:]
                challenge = output.strip().split('\n')[0].strip()
                print(f'CHALLENGE: {challenge}')
                set_challenge(challenge)
                print(f'CHALLENGE SET: {challenge}')
                time.sleep(30)  # wait challege is set
                input_queue.append('')
                stage = 'done'
            elif "isn't close to expiry" in output:
                input_queue.append('1')
                stage = 'done'

        # Sleep for a short duration before reading the next line
        time.sleep(0.1)

        # Check if the process has finished
        if process.poll() is not None:
            output_line = process.stdout.read()

            # Put the output into the queue
            print(f"Output: {output_line.strip()}")
            break


def main():
    # set_challenge('test')
    # exit()

    process = multiprocessing.Process(target=certbot)
    process.start()
    process.join()
    exit()


if __name__ == '__main__':
    main()

