def getHtml(otp):
    return f"""
  <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OTP Verification</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            width: 100% !important;
            -webkit-text-size-adjust: 100%;
            -ms-text-size-adjust: 100%;
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
        }}
        .container {{
            width: 100%;
            max-width: 600px;
            margin: 0 auto;
            background: #ffffff;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            padding: 20px;
        }}
        h1 {{
            color: #333333;
            font-size: 24px;
            text-align: center;
        }}
        p {{
            font-size: 16px;
            color: #555555;
            line-height: 1.5;
        }}
        .otp {{
            font-size: 32px;
            font-weight: bold;
            color: #007bff;
            text-align: center;
            margin: 20px 0;
        }}
        .footer {{
            text-align: center;
            font-size: 14px;
            color: #999999;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Your OTP Code</h1>
        <p>Hello,</p>
        <p>Your One-Time Password (OTP) for verification is:</p>
        <input value="{otp}" class="otp" disabled id="otp" />
        <p>Please enter this OTP in the application to proceed.</p>
        <p>This OTP is valid for 5 minutes. If you did not request this, please ignore this email.</p>
        <div class="footer">
            <p>Thank you!</p>
            <p>The Team</p>
        </div>
    </div>
</body>
</html>

  """