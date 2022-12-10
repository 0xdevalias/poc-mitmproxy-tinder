# poc-mitmproxy-tinder

https://chat.openai.com/chat

```
Write some python code that makes a MITM proxy that can capture and modify requests being made to the tinder API, while passing through all other data unmodified. It needs to be able to work with HTTPS data, and we will need to be able to generate and install a trusted root certificate into an iOS device and configure it to send data through this proxy.

Use the mitmproxy library.
```

- https://github.com/mitmproxy/mitmproxy
  - > An interactive TLS-capable intercepting HTTP proxy for penetration testers and software developers. 
- https://docs.mitmproxy.org/stable/api/events.html
- https://docs.mitmproxy.org/stable/api/mitmproxy/http.html#HTTPFlow
  - https://docs.mitmproxy.org/stable/api/mitmproxy/http.html#Request
  - https://docs.mitmproxy.org/stable/api/mitmproxy/http.html#Response
- https://docs.mitmproxy.org/stable/howto-ignoredomains/

## Running the script

```
mitmweb --allow-hosts '^api\.gotinder\.com$' --scripts poc-mitmproxy-tinder.py
```

## Installing the certificate on iOS

To install the mitmproxy certificate on an iOS device, you can use the following steps:

- Start the mitmproxy proxy on your computer and make sure it is listening on the correct interface and port.
- On the iOS device, go to the "Settings" app and open the "Wi-Fi" settings.
- Tap on the info (i) icon next to the Wi-Fi network you are currently connected to.
- Scroll down to the "HTTP Proxy" section and tap on "Manual".
- In the "Server" field, enter the IP address of the computer running mitmproxy. In the "Port" field, enter the port number that mitmproxy is listening on.
- Tap on "Save" to save the proxy settings.
- Open a web browser on the iOS device and navigate to http://mitm.it. This will download and install the mitmproxy certificate on the device.
- Once the certificate is installed, you can configure apps on the device to use the mitmproxy proxy. To do this, go to the "Settings" app and open the app's settings. Look for a "Proxy" or "Network" section, where you can enter the mitmproxy proxy settings (IP address and port) and enable the proxy.
- After following these steps, the iOS device should be configured to use the mitmproxy proxy, allowing you to intercept and modify HTTPS traffic. You may need to restart the device or the app for the proxy settings to take effect.
