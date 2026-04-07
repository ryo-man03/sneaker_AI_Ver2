// file: src/types/navigation.ts
export type AppPage =
  | 'dashboard'
  | 'search'
  | 'detail'
  | 'closet'
  | 'wishlist'
  | 'portfolio'
  | 'market'
  | 'stocks'
  | 'notifications'
  | 'profile'
  | 'buyscore'
  | 'admin'
  | 'dataops'

export type NavSection = {
  label: string
  items: Array<{
    key: AppPage
    label: string
    icon: string
    badge?: string
    tone?: 'default' | 'alert'
  }>
}
