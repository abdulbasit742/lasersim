// Live beam state management foundation

export interface BeamState {
  mode: string;
  power: number;
  stability: number;
}

export const initialBeamState: BeamState = {
  mode: 'unknown',
  power: 0,
  stability: 0,
};
