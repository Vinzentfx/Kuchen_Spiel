# Global Leaderboard Setup (Firebase — free)

Takes about 3 minutes.

## 1. Create a Firebase project
1. Go to https://console.firebase.google.com
2. Click **Add project** → give it any name → click through the prompts
3. On the project dashboard, click **Build → Realtime Database** in the left sidebar
4. Click **Create Database** → choose any region → select **Start in test mode** → Enable

## 2. Copy your database URL
It looks like:
```
https://your-project-name-default-rtdb.firebaseio.com
```
Copy it from the top of the Realtime Database page.

## 3. Paste it into index.html
Open `index.html` and find this line near the top of the `<script>` block:
```js
const FIREBASE_URL = '';
```
Replace it with your URL:
```js
const FIREBASE_URL = 'https://your-project-name-default-rtdb.firebaseio.com';
```

## 4. Done
Now anyone in the world can submit scores and see the leaderboard — no server needed.
The local `server.py` is still used as fallback when `FIREBASE_URL` is empty.

## Notes
- Test mode rules expire after 30 days. To make them permanent, set rules to:
  ```json
  { "rules": { ".read": true, ".write": true } }
  ```
  in **Realtime Database → Rules**.
- The free Spark plan supports 1 GB storage and 10 GB/month transfer — more than enough for a game leaderboard.
