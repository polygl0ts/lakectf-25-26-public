use glam::{Vec3};
use std::io::Cursor;

use crate::physics::BoxCollider;
use crate::reader::{read_f32, read_i32, read_quat, read_u16, read_vec3};

const CONFIG_BYTES: &[u8] = include_bytes!("../game_config.dat");

// ---------- Struct Definitions ----------
#[derive(Debug, Clone)]
pub struct PlayerData {
    pub speed: f32,
    pub gravity: f32,
    pub jump_height: f32,
    pub collider_size: Vec3,
}

#[derive(Debug, Clone)]
pub struct Level {
    pub _level_id: u16,
    pub spawn_area: BoxCollider,
    pub flag_area: BoxCollider,
    pub colliders: Vec<BoxCollider>,
}

#[derive(Debug, Clone)]
pub struct GameConfig {
    pub fixed_delta_time: f32,
    pub player_data: PlayerData,
    pub levels: Vec<Level>,
}

// ---------- Loading Function ----------


#[inline(never)]
fn read_collider(cursor: &mut Cursor<&[u8]>) -> Result<BoxCollider, Box<dyn std::error::Error>> {
    let position = read_vec3(cursor)?;
    let rotation = read_quat(cursor)?;
    let size = read_vec3(cursor)?;
    Ok(BoxCollider {
        position,
        rotation,
        size,
    })
}

#[inline(never)]
fn read_player_data(cursor: &mut Cursor<&[u8]>) -> Result<PlayerData, Box<dyn std::error::Error>> {
    let speed = read_f32(cursor)?;
    let gravity = read_f32(cursor)?;
    let jump_height = read_f32(cursor)?;
    let collider_size = read_vec3(cursor)?;

    Ok(PlayerData {
        speed,
        gravity,
        jump_height,
        collider_size,
    })
}

#[inline(never)]
fn read_level(cursor: &mut Cursor<&[u8]>) -> Result<Level, Box<dyn std::error::Error>> {
    let level_id = read_u16(cursor)?;
    let spawn_area = read_collider(cursor)?;
    let flag_area = read_collider(cursor)?;

    let colliders_count = read_i32(cursor)?;
    let mut colliders = Vec::with_capacity(colliders_count as usize);
    for _ in 0..colliders_count {
        colliders.push(read_collider(cursor)?);
    }

    Ok(Level {
        _level_id: level_id,
        spawn_area,
        flag_area,
        colliders,
    })
}

pub fn load() -> Result<GameConfig, Box<dyn std::error::Error>> {
    let mut cursor = Cursor::new(CONFIG_BYTES);

    let fixed_delta_time = read_f32(&mut cursor)?;
    let player_data = read_player_data(&mut cursor)?;

    let levels_count = read_i32(&mut cursor)?;
    let mut levels = Vec::with_capacity(levels_count as usize);
    for _ in 0..levels_count {
        levels.push(read_level(&mut cursor)?);
    }

    Ok(GameConfig {
        fixed_delta_time,
        player_data,
        levels,
    })
}
