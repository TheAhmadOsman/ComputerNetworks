# Simple Web Server

For this project you are going to write a simple web server using Python sockets only (i.e. no Flask, not even http.server). Your server should have the following functionality:

1. Bind to TCP port **4300** on **127.0.0.2** and accept 1 request at a time.
2. Serve a single file, *alice30.txt*.
3. Log details of each incoming request to *webserver.log*.
4. Return *405 Method Not Allowed* error for any method other than *GET*
5. Return *404 Not Found* error for any request other than */alice30.txt*.
6. Send the content of *alice30.txt* to the client along with proper response header.

## Request

A typical request header sent by a browser (Chrome in this case) looks as follows:

```
GET /alice30.txt HTTP/1.1
Host: 127.0.0.2:4300
Connection: keep-alive
Pragma: no-cache
Cache-Control: no-cache
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8
Accept-Encoding: gzip, deflate, br
Accept-Language: en-US,en;q=0.9

```

Use `curl` to initiate a *POST* request and see a 405 error:

```
curl -X POST http://127.0.0.2:4300/alice30.txt
```

## Log

Log file should contain the following information:

1. Time of the request.
2. Requested file.
3. IP address of the client.
4. Browser vendor and version.

```
2018-11-05 09:10:52.906984 | /alice.txt | 127.0.0.1 | Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36
2018-11-05 09:12:18.072352 | /alice30.txt | 127.0.0.1 | Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36
2018-11-05 09:15:00.526359 | /alice.txt | 127.0.0.1 | Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36
2018-11-05 09:21:58.869701 | /alice.txt | 127.0.0.1 | Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36
2018-11-05 09:22:06.622828 | /alice30.txt | 127.0.0.1 | Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36
```

## Response

Your server must include the following headers in the response:

1. HTTP version: 1.1
2. Response code: 200 OK
3. `Content-Length`: length of *alice30.txt*.
4. `Content-Type`: plain text (**not** html).
5. `Date`: current date
6. `Last-Modified`: Friday, August 29, 2018 11:00 AM
7. `Server`: must include **your name**

The response header sent by your server should look as follows (date and server are going to be different):

```
HTTP/1.1 200 OK
Content-Length: 148545
Content-Type: text/plain; charset=utf-8
Date: Sun Nov  4 23:25:40 2018
Last-Modified: Wed Aug 29 11:00:00 2018
Server: CS430-ROMAN

```

## References

* [RFC 7231 - Hypertext Transfer Protocol (HTTP/1.1): Semantics and Content](https://tools.ietf.org/html/rfc7231)

* [Request header - MDN Web Docs Glossary: Definitions of Web-related terms | MDN](https://developer.mozilla.org/en-US/docs/Glossary/Request_header)

* [Response header - MDN Web Docs Glossary: Definitions of Web-related terms | MDN](https://developer.mozilla.org/en-US/docs/Glossary/Response_header)

* [Alice's Adventures in Wonderland](www.umich.edu/~umfandsf/other/ebooks/alice30.txt)
