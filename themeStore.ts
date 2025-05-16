import { atom } from 'nanostores';

export interface ThemeState {
  theme: 'light' | 'dark';
}

export const themeStore = atom<ThemeState>({
  theme: 'dark'
});

export const useThemeStore = () => {
  return {
    theme: themeStore.get().theme,
    setTheme: (theme: 'light' | 'dark') => {
      themeStore.set({ theme });
    }
  };
}; 