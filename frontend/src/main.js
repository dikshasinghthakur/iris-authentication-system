import './style.css'

const API_URL = 'https://iris-authentication-system-aa69.onrender.com'

document.querySelector('#app').innerHTML = `
  <div class="container">
    <header>
      <h1>👁️ Iris Authentication System</h1>
      <p>Secure biometric authentication using iris recognition</p>
    </header>

    <main>
      <section class="camera-card">
        <video id="camera" autoplay playsinline></video>
        <canvas id="canvas" hidden></canvas>

        <div class="camera-buttons">
          <button id="startCamera">📷 Start Camera</button>
          <button id="capture">Capture Iris</button>
        </div>

        <p id="cameraStatus">Camera is not started</p>
      </section>

      <section class="actions">
        <div class="card">
          <h2>👤 Enroll</h2>
          <input id="username" type="text" placeholder="Enter username">
          <input id="email" type="email" placeholder="Enter email">
          <button id="enroll">Enroll User</button>
        </div>

        <div class="card">
          <h2>🔐 Verify</h2>
          <input id="verifyUsername" type="text" placeholder="Username">
          <button id="verify">Verify Identity</button>
        </div>

        <div class="card">
          <h2>🔎 Identify</h2>
          <button id="identify">Identify User</button>
        </div>
      </section>

      <section class="result-card">
        <h2>System Result</h2>
        <pre id="result">Ready...</pre>
      </section>
    </main>
  </div>
`

const video = document.querySelector('#camera')
const canvas = document.querySelector('#canvas')
const result = document.querySelector('#result')
const cameraStatus = document.querySelector('#cameraStatus')

let capturedImage = null

document.querySelector('#startCamera').addEventListener('click', async () => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({
      video: true
    })

    video.srcObject = stream
    cameraStatus.textContent = 'Camera is running ✅'
  } catch (error) {
    cameraStatus.textContent = 'Camera access denied ❌'
    result.textContent = error.message
  }
})

document.querySelector('#capture').addEventListener('click', () => {
  if (!video.srcObject) {
    result.textContent = 'Please start the camera first.'
    return
  }

  canvas.width = video.videoWidth
  canvas.height = video.videoHeight

  const context = canvas.getContext('2d')
  context.drawImage(video, 0, 0)

  capturedImage = canvas.toDataURL('image/jpeg').split(',')[1]

  result.textContent = 'Iris image captured successfully ✅'
})

async function sendRequest(endpoint, data) {
  try {
    const response = await fetch(`${API_URL}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    })

    const responseData = await response.json()

    result.textContent = JSON.stringify(responseData, null, 2)

  } catch (error) {
    result.textContent = `Backend connection error:\n${error.message}`
  }
}

document.querySelector('#enroll').addEventListener('click', () => {
  const username = document.querySelector('#username').value
  const email = document.querySelector('#email').value

  if (!username || !email || !capturedImage) {
    result.textContent = 'Please enter username, email and capture an iris image.'
    return
  }

  sendRequest('/enroll', {
    username,
    email,
    image: capturedImage
  })
})

document.querySelector('#verify').addEventListener('click', () => {
  const username = document.querySelector('#verifyUsername').value

  if (!username || !capturedImage) {
    result.textContent = 'Please enter username and capture an iris image.'
    return
  }

  sendRequest('/verify', {
    username,
    image: capturedImage
  })
})

document.querySelector('#identify').addEventListener('click', () => {
  if (!capturedImage) {
    result.textContent = 'Please capture an iris image first.'
    return
  }

  sendRequest('/identify', {
    image: capturedImage
  })
})