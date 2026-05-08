use glam::{Quat, Vec3};

use crate::game_config::{GameConfig, Level};
use crate::physics::*;
use crate::replay::{FrameRecord, PlayerActions, PlayerRecord, Replay};

#[derive(Debug)]
pub struct Simulation<'a> {
    current_step: usize,
    replay_data: &'a Replay,
    config: GameConfig,
    level: Level,

    previous_state: GameState,
}

#[derive(Debug)]
struct GameState {
    frame: FrameRecord,
    player_velocity: Vec3,
    has_flag: bool,
    run_successful: bool,
}

const EPS: f32 = 1e-5;
fn roughly_equal(a: Vec3, b: Vec3) -> bool {
    (a - b).length() < EPS
}

const MAX_NUM_STEPS: usize = 10000;

impl<'a> Simulation<'a> {
    pub fn new(config: GameConfig, replay_data: &'a Replay) -> Self {
        let level = config.levels[replay_data.level_id as usize].clone();
        let spawn_position = level.spawn_area.position;
        Self {
            current_step: 0,
            replay_data: replay_data,
            config,
            level,
            previous_state: GameState {
                frame: FrameRecord {
                    player_record: PlayerRecord {
                        position: spawn_position,
                        rotation: Quat::IDENTITY,
                        player_actions: PlayerActions::NONE,
                        // is_grounded: false,
                    },
                },
                player_velocity: Vec3::ZERO,
                has_flag: false,
                run_successful: false,
            },
        }
    }

    pub fn run(&mut self) -> bool {
        println!("Starting simulation for replay with {} frames", self.replay_data.frames.len());
        if self.replay_data.frames.len() > MAX_NUM_STEPS {
            return false;
        }

        while self.current_step < self.replay_data.frames.len() {
            let mut current_state = GameState {
                frame: self.replay_data.frames[self.current_step].clone(),
                player_velocity: self.previous_state.player_velocity,
                has_flag: self.previous_state.has_flag,
                run_successful: false,
            };

            if !self.simulation_step(&mut current_state) {
                return false;
            }

            self.previous_state = current_state;
            self.current_step += 1;
        }

        if self.previous_state.run_successful {
            return true;
        }
        return false;
    }

    fn simulation_step(&self, current_state: &mut GameState) -> bool {
        let simulation_result = self.simulate_player(current_state);

        return simulation_result;
    }

    fn simulate_player(&self, game_state: &mut GameState) -> bool {
        let previous_player_position = self.previous_state.frame.player_record.position;
        let requested_player_position = game_state.frame.player_record.position;
        let player_actions = game_state.frame.player_record.player_actions;

        let move_x = if player_actions.is_set(PlayerActions::LEFT) {
            -1.
        } else if player_actions.is_set(PlayerActions::RIGHT) {
            1.
        } else {
            0.
        };
        let move_z = if player_actions.is_set(PlayerActions::BACKWARD) {
            -1.
        } else if player_actions.is_set(PlayerActions::FORWARD) {
            1.
        } else {
            0.
        };

        let input_dir = Vec3::X * move_x + Vec3::Z * move_z;
        let horizontal_move = game_state.frame.player_record.rotation
            * input_dir.normalize_or_zero()
            * self.config.player_data.speed
            * self.config.fixed_delta_time;

        let is_grounded = self.is_grounded();
        if is_grounded {
            if player_actions.is_set(PlayerActions::JUMP) {
                game_state.player_velocity.y =
                    (self.config.player_data.jump_height * -2. * self.config.player_data.gravity).sqrt();
            } else {
                game_state.player_velocity.y = 0.;
            }
        } else {
            game_state.player_velocity.y += self.config.player_data.gravity * self.config.fixed_delta_time;
        }
        let vertical_move = Vec3::Y * game_state.player_velocity.y * self.config.fixed_delta_time;
        let simulated_move = horizontal_move + vertical_move;

        let simulated_player_position =
            self.move_and_collide(game_state, previous_player_position, simulated_move);

        return roughly_equal(requested_player_position, simulated_player_position);
    }

    fn is_grounded(&self) -> bool {
        let player_collider = BoxCollider {
            position: self.previous_state.frame.player_record.position,
            rotation: self.replay_data.frames[self.current_step]
                .player_record
                .rotation,
            size: self.config.player_data.collider_size,
        };

        let check_distance = 0.05;
        let test_collider = BoxCollider {
            position: player_collider.position
                - Vec3::Y * (player_collider.size.y * 0.5 - 0.01 + check_distance),
            rotation: player_collider.rotation,
            size: Vec3::new(player_collider.size.x, 0.1, player_collider.size.z),
        };

        let result = check_box(&test_collider, &self.level.colliders);

        return result;
    }

    fn move_and_collide(
        &self,
        game_state: &mut GameState,
        previous_player_position: Vec3,
        simulated_move: Vec3,
    ) -> Vec3 {
        let mut simulated_player_position = previous_player_position;

        simulated_player_position += Vec3::X * simulated_move.x;
        simulated_player_position = self.resolve_collisions(game_state, simulated_player_position);

        simulated_player_position += Vec3::Y * simulated_move.y;
        simulated_player_position = self.resolve_collisions(game_state, simulated_player_position);

        simulated_player_position += Vec3::Z * simulated_move.z;
        simulated_player_position = self.resolve_collisions(game_state, simulated_player_position);

        return simulated_player_position;
    }

    fn resolve_collisions(&self, game_state: &mut GameState, mut target_pos: Vec3) -> Vec3 {
        let player_collider = BoxCollider {
            position: target_pos,
            rotation: self.replay_data.frames[self.current_step]
                .player_record
                .rotation,
            size: self.config.player_data.collider_size,
        };

        self.test_trigger_areas(game_state, &player_collider);

        let skin_width = 0.01;
        let hits = overlap_box(&player_collider, &self.level.colliders);
        for hit in hits {
            if let Some((dir, dist)) = compute_penetration(&player_collider, &hit) {
                if dist > 0.0005 {
                    target_pos += dir * (dist + skin_width);
                }
            }
        }

        return target_pos;
    }

    fn test_trigger_areas(&self, game_state: &mut GameState, player_collider: &BoxCollider) {
        if player_collider.overlaps(&self.level.spawn_area) {
            if game_state.has_flag {
                game_state.run_successful = true;
            }
        }
        if player_collider.overlaps(&self.level.flag_area) {
            game_state.has_flag = true;
        }
    }
}
