export const theme = {
  colors: {
    primary: {
      main: 'from-indigo-600 to-cyan-600',
      hover: 'from-indigo-700 to-cyan-700',
      text: 'text-indigo-600',
      border: 'border-indigo-600',
      light: 'from-indigo-50 via-white to-cyan-50'
    },
    error: {
      light: 'bg-red-50',
      text: 'text-red-500'
    },
    success: {
      light: 'bg-green-50',
      text: 'text-green-800'
    }
  },
  components: {
    button: {
      base: 'w-full py-3 rounded-lg font-medium transition-all duration-200 flex items-center justify-center',
      primary: 'bg-gradient-to-r from-indigo-600 to-cyan-600 text-white hover:opacity-90',
      outlined: 'border-2 border-indigo-600 text-indigo-600 hover:bg-indigo-50'
    },
    input: {
      base: 'w-full px-4 py-3 rounded-lg transition-all duration-200',
      default: 'bg-gray-50 border border-gray-200 focus:border-indigo-500 focus:bg-white focus:ring-2 focus:ring-indigo-200'
    },
    card: {
      base: 'bg-white rounded-2xl shadow-xl overflow-hidden'
    }
  }
};

export type Theme = typeof theme; 