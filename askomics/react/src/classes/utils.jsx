export default class Utils {

  isUrl(s) {
     var regexp = /(ftp|http|https):\/\/(\w+:{0,1}\w*@)?(\S+)(:[0-9]+)?(\/|\/([\w#!:.?+=&%@!\-\/]))?/
     return regexp.test(s);
  }

  truncate(string, n) {
    if (string.length > n) {
      return string.substring(0 ,n) + "..."
    } else {
      return string
    }
  }

  splitUrl(url) {
    let splitList = url.split('/')
    // take last elem
    let last = splitList[splitList.length - 1]
    let splitList2 = last.split('#')
    return splitList2[splitList2.length - 1]
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
}
