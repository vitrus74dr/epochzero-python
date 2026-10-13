import { useEffect, useState } from 'react'
import { getTheme, onThemeChange, toggleTheme, type Theme } from './theme'

export function useTheme(): [Theme, () => void] {
  const [theme, setThemeState] = useState<Theme>(getTheme)
  useEffect(() => {
    const off = onThemeChange(setThemeState)
    return () => { off() }
  }, [])
  return [theme, toggleTheme]
}
