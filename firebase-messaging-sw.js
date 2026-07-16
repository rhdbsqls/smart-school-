// firebase-messaging-sw.js
importScripts('https://www.gstatic.com/firebasejs/10.8.0/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/10.8.0/firebase-messaging-compat.js');

const firebaseConfig = {
    apiKey: "AIzaSyC4arfE-nLP8EYVk-SG2UDbGDmS9LNDONg",
    authDomain: "smart-school-office-f363d.firebaseapp.com",
    projectId: "smart-school-office-f363d",
    storageBucket: "smart-school-office-f363d.firebasestorage.app",
    messagingSenderId: "865154285976",
    appId: "1:865154285976:web:1536e5af340f1cf653ebed"
};

firebase.initializeApp(firebaseConfig);
const messaging = firebase.messaging();

messaging.onBackgroundMessage((payload) => {
    console.log('[Service Worker] 백그라운드 알림 수신:', payload);
    const notificationTitle = payload.notification.title || '스마트 교무실';
    const notificationOptions = {
        body: payload.notification.body,
        icon: '/static/icon.png'
    };
    self.registration.showNotification(notificationTitle, notificationOptions);
});