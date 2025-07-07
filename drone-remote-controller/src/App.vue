<script>
export default {
  onLaunch: function () {
    console.log('App Launch');
    
    // Check if Bluetooth is available
    uni.getSystemInfo({
      success: function(res) {
        console.log('System info:', res);
        if (!res.bluetoothEnabled) {
          uni.showModal({
            title: 'Bluetooth Required',
            content: 'Please enable Bluetooth to use this app.',
            showCancel: false
          });
        }
      }
    });
    
    // Set screen to stay on while app is running
    uni.setKeepScreenOn({
      keepScreenOn: true
    });
  },
  onShow: function () {
    console.log('App Show');
  },
  onHide: function () {
    console.log('App Hide');
    
    // Turn off screen lock when app is hidden
    uni.setKeepScreenOn({
      keepScreenOn: false
    });
  },
}
</script>

<style>
/* Global CSS */
page {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
  background-color: #f8f8f8;
  color: #333;
}

button {
  margin: 0;
  padding: 0;
  line-height: 1;
}

button::after {
  border: none;
}

/* Disable pull-down refresh */
page {
  overflow: hidden;
}

/* Disable text selection */
text {
  user-select: none;
}
</style>
