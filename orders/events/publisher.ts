import { SQSClient, SendMessageCommand } from "@aws-sdk/client-sqs";

const sqs = new SQSClient({});

function queueAddress(name: string) {
  return `https://sqs.us-east-1.amazonaws.com/111111111111/${name}`;
}

function chooseAddress(archive: boolean) {
  if (archive) return "https://sqs.us-east-1.amazonaws.com/111111111111/smoke-legacy";
  return "https://sqs.us-east-1.amazonaws.com/111111111111/smoke-orders";
}

export function publishOrder(body: string) {
  const address = queueAddress("smoke-orders");
  return sqs.send(new SendMessageCommand({ QueueUrl: address, MessageBody: body }));
}

export function publishLiteral(body: string) {
  return sqs.send(new SendMessageCommand({
    QueueUrl: "https://sqs.us-east-1.amazonaws.com/111111111111/smoke-orders",
    MessageBody: body,
  }));
}

export function publishSelected(archive: boolean, body: string) {
  const address = chooseAddress(archive);
  return sqs.send(new SendMessageCommand({ QueueUrl: address, MessageBody: body }));
}
