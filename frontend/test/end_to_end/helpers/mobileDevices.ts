import { devices } from '@playwright/test'

const { defaultBrowserType: _iosBrowser, ...iphone12 } = devices['iPhone 12']
const { defaultBrowserType: _androidBrowser, ...pixel5 } = devices['Pixel 5']

export const mobileDevices = [
  { name: 'iPhone 12', device: iphone12, isAndroid: false },
  { name: 'Pixel 5', device: pixel5, isAndroid: true },
] as const

export const shouldSkipMobileDevice = (mobileDevice, testInfo) =>
  mobileDevice.isAndroid && testInfo.project.use?.browserName === 'webkit'
