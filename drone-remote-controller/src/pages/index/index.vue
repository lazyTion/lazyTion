<template>
  <view class="container">
    <view class="header">
      <image class="logo" src="/static/images/drone.svg"></image>
      <text class="title">Drone Remote Controller</text>
      <view class="connection-status">
        <text class="status-text">{{ connectionStatus }}</text>
      </view>
    </view>
    
    <view class="bluetooth-section">
      <button class="scan-button" @click="startBluetoothDevicesDiscovery" :disabled="isScanning">
        {{ isScanning ? 'Scanning...' : 'Scan for Drones' }}
      </button>
      
      <view class="device-list" v-if="devices.length > 0">
        <view class="device-item" v-for="(device, index) in devices" :key="index" @click="connectToDevice(device)">
          <text class="device-name">{{ device.name || 'Unknown Device' }}</text>
          <text class="device-id">{{ device.deviceId }}</text>
        </view>
      </view>
      <view class="no-devices" v-else-if="!isScanning">
        <text>No devices found</text>
      </view>
    </view>
    
    <view class="controls" v-if="isConnected">
      <view class="control-section">
        <text class="section-title">Flight Controls</text>
        <view class="control-grid">
          <view class="control-row">
            <button class="control-button" @touchstart="sendCommand('up')" @touchend="sendCommand('stop')">Up</button>
          </view>
          <view class="control-row">
            <button class="control-button" @touchstart="sendCommand('left')" @touchend="sendCommand('stop')">Left</button>
            <button class="control-button" @touchstart="sendCommand('hover')" @touchend="sendCommand('stop')">Hover</button>
            <button class="control-button" @touchstart="sendCommand('right')" @touchend="sendCommand('stop')">Right</button>
          </view>
          <view class="control-row">
            <button class="control-button" @touchstart="sendCommand('down')" @touchend="sendCommand('stop')">Down</button>
          </view>
        </view>
      </view>
      
      <view class="control-section">
        <text class="section-title">Special Commands</text>
        <view class="special-controls">
          <button class="special-button" @click="sendCommand('takeoff')">Take Off</button>
          <button class="special-button" @click="sendCommand('land')">Land</button>
          <button class="special-button emergency" @click="sendCommand('emergency')">Emergency Stop</button>
        </view>
      </view>
      
      <view class="control-section">
        <text class="section-title">Rotation Controls</text>
        <view class="rotation-controls">
          <button class="rotation-button" @touchstart="sendCommand('rotateLeft')" @touchend="sendCommand('stop')">Rotate Left</button>
          <button class="rotation-button" @touchstart="sendCommand('rotateRight')" @touchend="sendCommand('stop')">Rotate Right</button>
        </view>
      </view>
    </view>
    
    <view class="disconnected-message" v-if="!isConnected && hasConnectedBefore">
      <text>Disconnected from drone. Please reconnect.</text>
      <button class="reconnect-button" @click="reconnect">Reconnect</button>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      isScanning: false,
      devices: [],
      connectedDeviceId: '',
      isConnected: false,
      hasConnectedBefore: false,
      connectionStatus: 'Not Connected',
      bluetoothAdapter: null,
      serviceId: '',
      characteristicId: '',
      buffer: []
    }
  },
  onLoad() {
    // Initialize Bluetooth when the page loads
    this.initBluetooth();
  },
  onUnload() {
    // Clean up Bluetooth connections when leaving the page
    this.closeBluetooth();
  },
  methods: {
    // Initialize Bluetooth
    initBluetooth() {
      uni.openBluetoothAdapter({
        success: (res) => {
          console.log('Bluetooth adapter opened successfully', res);
          this.bluetoothAdapter = res;
          this.listenBluetoothAdapterStateChange();
        },
        fail: (err) => {
          console.error('Failed to open Bluetooth adapter', err);
          uni.showToast({
            title: 'Please enable Bluetooth',
            icon: 'none'
          });
        }
      });
    },
    
    // Listen for Bluetooth adapter state changes
    listenBluetoothAdapterStateChange() {
      uni.onBluetoothAdapterStateChange((res) => {
        console.log('Bluetooth adapter state changed', res);
        if (!res.available) {
          this.isConnected = false;
          this.connectionStatus = 'Bluetooth Not Available';
          this.devices = [];
        }
      });
    },
    
    // Start scanning for Bluetooth devices
    startBluetoothDevicesDiscovery() {
      if (this.isScanning) return;
      
      this.isScanning = true;
      this.devices = [];
      
      uni.startBluetoothDevicesDiscovery({
        allowDuplicatesKey: false,
        success: (res) => {
          console.log('Started scanning for Bluetooth devices', res);
          this.onBluetoothDeviceFound();
          
          // Stop scanning after 10 seconds
          setTimeout(() => {
            this.stopBluetoothDevicesDiscovery();
          }, 10000);
        },
        fail: (err) => {
          console.error('Failed to start scanning for Bluetooth devices', err);
          this.isScanning = false;
          uni.showToast({
            title: 'Failed to scan for devices',
            icon: 'none'
          });
        }
      });
    },
    
    // Stop scanning for Bluetooth devices
    stopBluetoothDevicesDiscovery() {
      if (!this.isScanning) return;
      
      uni.stopBluetoothDevicesDiscovery({
        success: (res) => {
          console.log('Stopped scanning for Bluetooth devices', res);
          this.isScanning = false;
        },
        fail: (err) => {
          console.error('Failed to stop scanning for Bluetooth devices', err);
          this.isScanning = false;
        }
      });
    },
    
    // Handle Bluetooth device found event
    onBluetoothDeviceFound() {
      uni.onBluetoothDeviceFound((res) => {
        res.devices.forEach(device => {
          // Only add devices that have a name (to filter out unwanted devices)
          if (device.name || device.localName) {
            // Check if device is already in the list
            const isDuplicate = this.devices.some(d => d.deviceId === device.deviceId);
            if (!isDuplicate) {
              this.devices.push(device);
            }
          }
        });
      });
    },
    
    // Connect to a Bluetooth device
    connectToDevice(device) {
      this.stopBluetoothDevicesDiscovery();
      this.connectionStatus = 'Connecting...';
      
      uni.createBLEConnection({
        deviceId: device.deviceId,
        success: (res) => {
          console.log('Connected to device', res);
          this.connectedDeviceId = device.deviceId;
          this.isConnected = true;
          this.hasConnectedBefore = true;
          this.connectionStatus = 'Connected to ' + (device.name || 'Unknown Device');
          
          // Get services after connecting
          this.getBLEDeviceServices(device.deviceId);
        },
        fail: (err) => {
          console.error('Failed to connect to device', err);
          this.connectionStatus = 'Connection Failed';
          uni.showToast({
            title: 'Failed to connect to device',
            icon: 'none'
          });
        }
      });
    },
    
    // Get services for a Bluetooth device
    getBLEDeviceServices(deviceId) {
      uni.getBLEDeviceServices({
        deviceId: deviceId,
        success: (res) => {
          console.log('Device services', res);
          for (let i = 0; i < res.services.length; i++) {
            const service = res.services[i];
            // Look for a service that might be used for drone control
            // This is a placeholder - you would need to know the specific service UUID for your drone
            if (service.isPrimary) {
              this.serviceId = service.uuid;
              this.getBLEDeviceCharacteristics(deviceId, service.uuid);
              break;
            }
          }
        },
        fail: (err) => {
          console.error('Failed to get device services', err);
        }
      });
    },
    
    // Get characteristics for a Bluetooth service
    getBLEDeviceCharacteristics(deviceId, serviceId) {
      uni.getBLEDeviceCharacteristics({
        deviceId: deviceId,
        serviceId: serviceId,
        success: (res) => {
          console.log('Service characteristics', res);
          for (let i = 0; i < res.characteristics.length; i++) {
            const characteristic = res.characteristics[i];
            // Look for a characteristic that can be written to
            if (characteristic.properties.write) {
              this.characteristicId = characteristic.uuid;
              console.log('Found writable characteristic', characteristic);
              break;
            }
            // Also look for a characteristic that can notify
            if (characteristic.properties.notify || characteristic.properties.indicate) {
              uni.notifyBLECharacteristicValueChange({
                deviceId: deviceId,
                serviceId: serviceId,
                characteristicId: characteristic.uuid,
                state: true,
                success: () => {
                  console.log('Enabled notifications for characteristic');
                  this.onBLECharacteristicValueChange();
                }
              });
            }
          }
        },
        fail: (err) => {
          console.error('Failed to get service characteristics', err);
        }
      });
    },
    
    // Handle characteristic value changes
    onBLECharacteristicValueChange() {
      uni.onBLECharacteristicValueChange((res) => {
        console.log('Characteristic value changed', res);
        // Process the data received from the drone
        const value = new Uint8Array(res.value);
        // Process the data according to your drone's protocol
        console.log('Received data from drone:', value);
      });
    },
    
    // Send a command to the drone
    sendCommand(command) {
      if (!this.isConnected || !this.characteristicId || !this.serviceId) {
        console.error('Cannot send command - not connected or missing service/characteristic');
        return;
      }
      
      console.log('Sending command:', command);
      
      // Convert the command to a byte array according to your drone's protocol
      // This is a placeholder - you would need to know the specific protocol for your drone
      let buffer;
      
      switch (command) {
        case 'takeoff':
          buffer = new Uint8Array([0x01, 0x00, 0x00, 0x00]);
          break;
        case 'land':
          buffer = new Uint8Array([0x02, 0x00, 0x00, 0x00]);
          break;
        case 'up':
          buffer = new Uint8Array([0x03, 0x01, 0x00, 0x00]);
          break;
        case 'down':
          buffer = new Uint8Array([0x03, 0x02, 0x00, 0x00]);
          break;
        case 'left':
          buffer = new Uint8Array([0x04, 0x01, 0x00, 0x00]);
          break;
        case 'right':
          buffer = new Uint8Array([0x04, 0x02, 0x00, 0x00]);
          break;
        case 'rotateLeft':
          buffer = new Uint8Array([0x05, 0x01, 0x00, 0x00]);
          break;
        case 'rotateRight':
          buffer = new Uint8Array([0x05, 0x02, 0x00, 0x00]);
          break;
        case 'hover':
          buffer = new Uint8Array([0x06, 0x00, 0x00, 0x00]);
          break;
        case 'emergency':
          buffer = new Uint8Array([0xFF, 0x00, 0x00, 0x00]);
          break;
        case 'stop':
          buffer = new Uint8Array([0x00, 0x00, 0x00, 0x00]);
          break;
        default:
          console.error('Unknown command:', command);
          return;
      }
      
      uni.writeBLECharacteristicValue({
        deviceId: this.connectedDeviceId,
        serviceId: this.serviceId,
        characteristicId: this.characteristicId,
        value: buffer.buffer,
        success: (res) => {
          console.log('Command sent successfully', res);
        },
        fail: (err) => {
          console.error('Failed to send command', err);
          // If we fail to send a command, we might be disconnected
          if (err.errCode === 10006) {
            this.isConnected = false;
            this.connectionStatus = 'Disconnected';
          }
        }
      });
    },
    
    // Reconnect to the last connected device
    reconnect() {
      if (!this.connectedDeviceId) return;
      
      this.connectToDevice({ deviceId: this.connectedDeviceId });
    },
    
    // Close Bluetooth connection
    closeBluetooth() {
      if (this.connectedDeviceId) {
        uni.closeBLEConnection({
          deviceId: this.connectedDeviceId,
          success: (res) => {
            console.log('Closed BLE connection', res);
          }
        });
      }
      
      uni.closeBluetoothAdapter({
        success: (res) => {
          console.log('Closed Bluetooth adapter', res);
          this.isConnected = false;
          this.connectionStatus = 'Not Connected';
        }
      });
    }
  }
}
</script>

<style>
.container {
  display: flex;
  flex-direction: column;
  padding: 20rpx;
  height: 100vh;
  box-sizing: border-box;
}

.header {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20rpx 0;
  border-bottom: 1px solid #eee;
}

.logo {
  width: 120rpx;
  height: 120rpx;
  margin-bottom: 20rpx;
}

.title {
  font-size: 40rpx;
  font-weight: bold;
  color: #333;
}

.connection-status {
  margin-top: 10rpx;
  padding: 10rpx 20rpx;
  background-color: #f0f0f0;
  border-radius: 10rpx;
}

.status-text {
  font-size: 28rpx;
  color: #666;
}

.bluetooth-section {
  margin: 30rpx 0;
}

.scan-button {
  background-color: #007AFF;
  color: white;
  border-radius: 10rpx;
  padding: 20rpx 0;
  font-size: 32rpx;
}

.device-list {
  margin-top: 20rpx;
  border: 1px solid #eee;
  border-radius: 10rpx;
  max-height: 300rpx;
  overflow-y: auto;
}

.device-item {
  padding: 20rpx;
  border-bottom: 1px solid #eee;
}

.device-item:last-child {
  border-bottom: none;
}

.device-name {
  font-size: 32rpx;
  color: #333;
}

.device-id {
  font-size: 24rpx;
  color: #999;
  margin-top: 10rpx;
}

.no-devices {
  text-align: center;
  padding: 30rpx;
  color: #999;
}

.controls {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 30rpx;
}

.control-section {
  border: 1px solid #eee;
  border-radius: 10rpx;
  padding: 20rpx;
}

.section-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 20rpx;
}

.control-grid {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20rpx;
}

.control-row {
  display: flex;
  gap: 20rpx;
}

.control-button {
  width: 150rpx;
  height: 150rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f0f0f0;
  border-radius: 10rpx;
  font-size: 28rpx;
}

.special-controls {
  display: flex;
  justify-content: space-around;
}

.special-button {
  width: 200rpx;
  padding: 20rpx 0;
  background-color: #4CD964;
  color: white;
  border-radius: 10rpx;
  font-size: 28rpx;
}

.special-button.emergency {
  background-color: #FF3B30;
}

.rotation-controls {
  display: flex;
  justify-content: space-around;
}

.rotation-button {
  width: 200rpx;
  padding: 20rpx 0;
  background-color: #5856D6;
  color: white;
  border-radius: 10rpx;
  font-size: 28rpx;
}

.disconnected-message {
  margin-top: 30rpx;
  padding: 20rpx;
  background-color: #FFCC00;
  border-radius: 10rpx;
  text-align: center;
}

.reconnect-button {
  margin-top: 20rpx;
  background-color: #007AFF;
  color: white;
  border-radius: 10rpx;
  padding: 10rpx 0;
  font-size: 28rpx;
}
</style>
