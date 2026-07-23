// WebSocket hook foundation for live beam data

export function useBeamSocket(url: string) {
  return {
    status: 'ready',
    connect: () => {
      return new WebSocket(url);
    },
  };
}
