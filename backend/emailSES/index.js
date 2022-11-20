var aws = require("aws-sdk");
var ses = new aws.SES({ region: "us-east-1" });
exports.handler = async function (event) {
    const body = JSON.parse(event["Records"][0]["body"])
    console.log(body)
  var params = {
    Destination: {
      ToAddresses: body.EmailAddresses,
    },
    Message: {
      Body: {
        Text: { Data: body.ContentText },
      },

      Subject: { Data: body.Subject },
    },
    Source: "rabbakg3t7@gmail.com",
  };
 
  return ses.sendEmail(params).promise()
};