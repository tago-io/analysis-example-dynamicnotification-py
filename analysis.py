"""
Analysis Example
Sending dynamic notification

Send notifications using analysis. It's include example for Email, SMS and Push Notification to TagoRUN Users.
In order for this example to work, you must create an action by variable and set to run this analysis.
Once the action is triggered with your conditions, the data will be sent to this analysis.

Environment Variables
In order to use this analysis, you must setup the Environment Variable table.
account_token: Your account token. Check bellow how to get this.

Steps to generate an account_token:
1 - Enter the following link: https://admin.tago.io/account/
2 - Select your Profile.
3 - Enter Tokens tab.
4 - Generate a new Token with Expires Never.
5 - Press the Copy Button and place at the Environment Variables tab of this analysis.
"""
from tagoio_sdk import Analysis, Resources, Services
from tagoio_sdk.modules.Utils.envToJson import envToJson


def my_analysis(context, scope: list[dict]) -> None:
    if not scope:
        return print("This analysis must be triggered by an action.")

    # Get the environment variables.
    environment_variables = envToJson(context.environment)

    if not environment_variables.get("account_token"):
        return print('Missing "account_token" environment variable')
    elif len(environment_variables["account_token"]) != 36:
        return print('Invalid "account_token" in the environment variable')

    # Instance the Resources class
    resources = Resources()

    # Get the device ID from the scope and retrieve device information.
    device_id = scope[0]["device"]
    device_info = resources.devices.info(device_id)
    device_name = device_info["name"]

    # Get the device name and tags from the device.
    # [TAG KEY]    [TAG VALUE]
    # email        example@tago.io
    # phone        +1XXxxxxxxx
    # user_id      5f495ae55ff03d0028d39fc5
    email_tag = next(filter(lambda tag: tag["key"] == "email", device_info["tags"]), None)
    phone_tag = next(filter(lambda tag: tag["key"] == "phone", device_info["tags"]), None)
    user_id_tag = next(filter(lambda tag: tag["key"] == "user_id", device_info["tags"]), None)

    # This is just a generic example how to get this information. You can get data from a device, search in tags, or any other way of correlation you have.
    # For example, you can get the email directly from the user_id if it was specified:
    # email = await resources.run.user_info(user_id_tag["value"]).get("email")

    # Instance the SMS and Email service using the analysis token from the context.
    email_service = Services({"token": context.token}).email
    sms_service = Services({"token": context.token}).sms

    # Send the notifications and output the results to the analysis console.
    message = f"You received a notification for the device: {device_name}. Variable: {scope[0]['variable']}, Value: {scope[0]['value']}"

    if email_tag:
        result = email_service.send({"to": email_tag["value"], "subject": "Notification alert", "message": message})
        print(result)
    else:
        print("Email not found for this device.")

    if phone_tag:
        result = sms_service.send({"to": phone_tag["value"], "message": message,})
        print(result)
    else:
        print("Phone number not found for this device.")

    if user_id_tag:
        result = resources.run.notificationCreate(user_id_tag["value"], {"title": "Notification Alert", "message": message})
        print(result)
    else:
        print("User ID not found for this device.")


# The analysis token in only necessary to run the analysis outside TagoIO
Analysis.use(my_analysis, params={"token": "MY-ANALYSIS-TOKEN-HERE"})
