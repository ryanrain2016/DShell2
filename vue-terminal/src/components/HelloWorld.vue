<template>
  <div>
  <input type="text" :value="hostinfo.host" placeholder="host">
  <input type="number" :value="hostinfo.port" placeholder="port">
  <input type="text" :value="hostinfo.username" placeholder="username">
  <input type="password" :value="hostinfo.passwd" placeholder="password">
  <button @click="connect" :disabled="websocket && websocket.readyState == 2">连接</button>
  <div id='terminal'></div>
  </div>
</template>

<script>
import { Terminal } from 'xterm'
import '../../node_modules/xterm/dist/xterm.css'
import * as fit from 'xterm/lib/addons/fit/fit'
Terminal.applyAddon(fit)

export default {
  name: 'HelloWorld',
  data () {
    return {
      terminal: null,
      websocket: null,
      hostinfo: {
        host: '',
        port: '',
        username: '',
        passwd: ''
      }
    }
  },
  mounted () {
    this.terminal = new Terminal({
      cursorBlink: 5,
      scrollback: 100,
      tabStopWidth: 4
    })
    this.terminal.open(document.getElementById('terminal'))
    this.terminal.fit()
    this.terminal.on('data', (data) => {
      if (!data) return
      this.websocket.send(data)
    })
  },
  methods: {
    connect () {
      this.websocket = new WebSocket('ws://localhost:8999/ws/ssh')
      this.websocket.onopen = () => {
        this.websocket.send(JSON.stringify(this.hostinfo))
      }
      this.websocket.onmessage = (message) => {
        this.terminal.write(message.data)
      }
      this.websocket.onerror = () => {
        this.terminal.write('something error, disconnected')
        this.websocket = null
      }
      this.websocket.onclose = () => {
        this.terminal.write('disconnected')
        this.websocket = null
      }
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>
