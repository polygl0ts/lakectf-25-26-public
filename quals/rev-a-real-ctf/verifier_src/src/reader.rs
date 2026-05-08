use byteorder::{LittleEndian, ReadBytesExt};
use glam::{Quat, Vec3};
use std::io::{Cursor, Result};

#[inline(never)]
pub fn read_f32(cursor: &mut Cursor<&[u8]>) -> Result<f32> {
    let value = cursor.read_f32::<LittleEndian>()?;
    Ok(value)
}

#[inline(never)]
pub fn read_u8(cursor: &mut Cursor<&[u8]>) -> Result<u8> {
    let value = cursor.read_u8()?;
    Ok(value)
}

#[inline(never)]
pub fn read_u16(cursor: &mut Cursor<&[u8]>) -> Result<u16> {
    let value = cursor.read_u16::<LittleEndian>()?;
    Ok(value)
}

#[inline(never)]
pub fn read_u64(cursor: &mut Cursor<&[u8]>) -> Result<u64> {
    let value = cursor.read_u64::<LittleEndian>()?;
    Ok(value)
}

#[inline(never)]
pub fn read_i32(cursor: &mut Cursor<&[u8]>) -> Result<i32> {
    let value = cursor.read_i32::<LittleEndian>()?;
    Ok(value)
}

#[inline(never)]
pub fn read_vec3(cursor: &mut Cursor<&[u8]>) -> Result<Vec3> {
    let x = read_f32(cursor)?;
    let y = read_f32(cursor)?;
    let z = read_f32(cursor)?;
    Ok(Vec3 { x, y, z })
}

#[inline(never)]
pub fn read_quat(cursor: &mut Cursor<&[u8]>) -> Result<Quat> {
    let x = read_f32(cursor)?;
    let y = read_f32(cursor)?;
    let z = read_f32(cursor)?;
    let w = read_f32(cursor)?;
    Ok(Quat::from_xyzw(x, y, z, w))
}