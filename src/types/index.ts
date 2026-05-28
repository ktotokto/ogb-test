import { st } from "vue-router/dist/router-CWoNjPRp.mjs"

export interface UserDetails {
  id: string
  username: string
  email: string
  avatar_url: string
  banner_url: string
  bio: string
  is_online: boolean
  last_seen: string
}

export interface Player {
  id: string
  is_active: boolean
  joined_at: string
  role: 'creator' | 'member' | string
  session_id: string
  user_id: string
  user: UserDetails
}

export interface AvatarItem {
  userId: string;
  url: string; 
}

export interface OptionsSession {
    name: string,
    isPrivate: boolean,
    maxPlayers: number
}

export interface GameSettings {
  backgroundColor: string
  boardRotation: number
  gridEnabled: boolean
  gridSize: number
  snapToGrid: boolean
}

interface GameState {
  drawings: Drawing[]
  handCards: CardObject[]
  objects: GameObject[] 
  settings: GameSettings
}

export interface Drawing {
    color: string
    createdAt: string
    id: string
    points: {
        x: number,
        y: number
    }[]
    size: number
    type: string
    userId: string
}

export interface GameSession {
  created_at: string
  creator_id: string
  id: string
  is_private: boolean
  max_players: number
  name: string
  players: Player[]
  state: GameState
  updated_at: string
}

export interface GameObject {
    id: string
    label: string
    position: {
        x: number,
        y: number
    }
    resizable: boolean
    rotation: number
    type: 'card' | 'deck' | string
    width: number
    height: number
}

export interface CardObject extends GameObject {
  type: 'card'
  faceUp: boolean
  frontImage: string | null
  backImage: string | null
}

export interface DeckObject extends GameObject {
  type: 'deck'
  cardCount: number
  cards: CardObject[] 
}

export interface DeckData {
    cardCount: number
    cards: CardObject[]
    id: string
    label: string
}