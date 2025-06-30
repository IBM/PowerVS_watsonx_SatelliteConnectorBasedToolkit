# Running chatbot on Power virtual server

User needs to deploy any of web application server to deploy chatbot ui, here we will be using nginx to deploy chatbot application.

1) Pull the latest code and update vite.config.js with the desired port on which UI chat application needs to run. The vite.config.js could be found in location:
```
powervs_watsonx_toolkit/chatbot_ui
```
2) Update .env file with chatbot api specific protocol, hostname and port.
Here are the list of available ports on IBM Power Virtual Server refer :https://cloud.ibm.com/docs/power-iaas?topic=power-iaas-network-security
3) **Build the Application for Production**:
Run the following command to generate the dist folder:
```
npm run build
```

**Deploy application on webserver(nginx)**
1) Install nginx on Power virtual server 
```
sudo dnf install -y nginx
```
2) Verify if nginx is installed successfully
```
nginx -v
```
3) Copy the contents of the **dist/** folder to the web root directory (e.g., /var/www/html or a custom location):
```
sudo cp -r dist/* /var/www/html/
```
4) Once nginx is installed, update the UI application port and hostname in nginx configuration: **/etc/nginx/nginx.conf**.
```
server {
    listen <port_number>;
    server_name <host_name>;

    root /var/www/html;
    index index.html;

        location / {
            try_files $uri /index.html;
        }
}
```
5) Restart nginx:
```
sudo systemctl restart nginx
```
6) Once nginx is restarted you can expect UI to be running on specified port, example:
```
http://<powervs-ipaddress>:<port_number>
```


# Running development container application:
- Update Dockerfile.dev with valid hostname on which chatbot api server is running: *VITE_CHATBOT_API_HOST*
- docker build -f Dockerfile.dev -t docker_chatbot_dev:v1 .
- docker run --name docker_chatbot_dev -p _*port_number*_:_*port_number*_ docker_chatbot_dev:v1 (replace _*port_number*_ with valid port_number)

Your application will be up and running on port <port_number> (_*port_number*_ is same as the one mentioned in vite.config.js)

# Running production container application:
- Update Dockerfile.prod with valid hostname on which chatbot api server is running: *VITE_CHATBOT_API_HOST*
- docker build -f Dockerfile.prod -t docker_chatbot_prod:v1 .
- docker run --name docker_chatbot_prod -p _*port_number*_:_*port_number*_ docker_chatbot_prod:v1 (replace _*port_number*_ with valid port_number)

Your application will be up and running on port <port_number> (_*port_number*_ is same as the one mentioned in vite.config.js)

# To modify port in production:
- Update *chatbot_ui/Dockerfile.prod* to expose desired port details
- This also needs update to ngnix.conf in the container
