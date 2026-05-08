mod reader;
mod game_config;
mod physics;
mod replay;
mod simulator;

use axum::{Router, body::Bytes, routing::post};
use std::fs;
use std::io::Cursor;

use crate::replay::read_replay;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let game_config = game_config::load()?;

    let app = Router::new().route(
        "/",
        post(|body: Bytes| async move {
            println!("New request received");

            let mut cursor = Cursor::new(body.as_ref());
            // match read_replay_from_cursor(cursor) {
            match read_replay(&mut cursor) {
                Ok(replay) => {
                    if replay.level_id as usize >= game_config.levels.len() {
                        println!("Invalid level id");
                        return format!("Invalid level id");
                    }

                    let mut simulation = simulator::Simulation::new(game_config, &replay);
                    let simulation_result = simulation.run();

                    if simulation_result {
                        if replay.level_id == 1 {
                            let flag = fs::read_to_string("./flag.txt");
                            match flag {
                                Ok(flag_content) => {
                                    println!("Simulation successful");
                                    format!("Simulation successful ! A small present for you: {}", flag_content)
                                }
                                Err(_) => {
                                    println!("Simulation successful");
                                    format!("Simulation successful ! A small present for: <no flag file>")
                                }
                            }
                        } else {
                            println!("Simulation successful");
                            format!("Simulation successful but no flag for you !")
                        }
                    } else {
                        println!("Simulation failed");
                        format!("Simulation failed")
                    }
                }
                Err(err) => {
                    println!("Failed to parse");
                    format!("Failed to parse replay: {}", err)
                }
            }
        }),
    );

    let listener = tokio::net::TcpListener::bind("0.0.0.0:8533").await.unwrap();
    axum::serve(listener, app).await.unwrap();

    Ok(())
}
