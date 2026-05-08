use glam::{Quat, Vec3};
use std::io::{self, Cursor, Result};

use crate::reader::*;

const MAGIC: u64 = 0x42414E414E41; // 'BANANA'
const VERSION: u16 = 1;

#[derive(Debug)]
pub struct Replay {
    pub level_id: u16,
    pub frames: Vec<FrameRecord>,
}

#[derive(Debug, Clone)]
pub struct FrameRecord {
    pub player_record: PlayerRecord,
}

#[derive(Debug, Clone)]
pub struct PlayerRecord {
    pub position: Vec3,
    pub rotation: Quat,
    pub player_actions: PlayerActions,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct PlayerActions(u8);

impl PlayerActions {
    pub const NONE: Self = Self(0);
    pub const JUMP: Self = Self(1 << 0);
    pub const FORWARD: Self = Self(1 << 1);
    pub const BACKWARD: Self = Self(1 << 2);
    pub const LEFT: Self = Self(1 << 3);
    pub const RIGHT: Self = Self(1 << 4);

    pub fn from_u8(mask: u8) -> Self {
        Self(mask)
    }

    pub fn is_set(&self, action: PlayerActions) -> bool {
        (self.0 & action.0) != 0
    }
}

pub fn read_replay(cursor: &mut Cursor<&[u8]>) -> Result<Replay> {
    let magic = read_u64(cursor)?;
    if magic != MAGIC {
        return Err(io::Error::new(io::ErrorKind::InvalidData, "Invalid data"));
    }

    let version = read_u16(cursor)?;
    if version != VERSION {
        return Err(io::Error::new(io::ErrorKind::InvalidData, "Invalid data"));
    }

    let level_id = read_u16(cursor)?;
    let frame_count = read_u16(cursor)?;

    // --- FRAMES ---
    let mut frames = Vec::with_capacity(frame_count as usize);
    for _ in 0..frame_count {
        let position = read_vec3(cursor)?;
        let rotation = read_quat(cursor)?;
        let player_actions = PlayerActions::from_u8(read_u8(cursor)?);

        frames.push(FrameRecord {
            player_record: PlayerRecord {
                position,
                rotation,
                player_actions,
            },
        });
    }

    Ok(Replay { frames, level_id })
}
