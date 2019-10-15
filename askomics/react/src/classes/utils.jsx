export default class Utils {

  constructor () {

  }

  humanFileSize (bytes, si) {
    let thresh = si ? 1000 : 1024
    if (Math.abs(bytes) < thresh) {
      return bytes + ' B'
    }
    let units = si ? ['kB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'] : ['KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'ZiB', 'YiB']
    let u = -1
    do {
      bytes /= thresh
      ++u
    } while (Math.abs(bytes) >= thresh && u < units.length - 1)
    return bytes.toFixed(1) + ' ' + units[u]
  }

  humanDate (date) {
    let event = new Date(date * 1000)
    return event.toUTCString()
  }

  objectHaveKeys(obj, level, ...rest) {
    if (obj === undefined) return false
    if (rest.length == 0 && obj.hasOwnProperty(level)) return true
    return this.objectHaveKeys(obj[level], ...rest)
  }
}
