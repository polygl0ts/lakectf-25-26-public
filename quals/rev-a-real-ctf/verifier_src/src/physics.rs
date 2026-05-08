/// EVERYTHING BELOW IS A SIMPLIFIED PHYSICS MODULE FOR COLLISION
use glam::{Quat, Vec3};

#[derive(Debug, Clone, Copy)]
pub struct BoxCollider {
    pub position: Vec3,
    pub rotation: Quat,
    pub size: Vec3,
}

impl BoxCollider {
    /// Returns the 3 local axes of this OBB in world space.
    fn axes(&self) -> [Vec3; 3] {
        [
            self.rotation * Vec3::X,
            self.rotation * Vec3::Y,
            self.rotation * Vec3::Z,
        ]
    }

    /// Check if this box overlaps another box (simplified OBB check)
    pub fn overlaps(&self, other: &BoxCollider) -> bool {
        let half_self = self.size * 0.5;
        let half_other = other.size * 0.5;

        let axes_a = [
            self.rotation * Vec3::X,
            self.rotation * Vec3::Y,
            self.rotation * Vec3::Z,
        ];

        let axes_b = [
            other.rotation * Vec3::X,
            other.rotation * Vec3::Y,
            other.rotation * Vec3::Z,
        ];

        let d = other.position - self.position;

        // Test the 15 possible separating axes
        for &axis in axes_a.iter().chain(axes_b.iter()) {
            let projection_self = half_self.x * axis.dot(axes_a[0]).abs()
                + half_self.y * axis.dot(axes_a[1]).abs()
                + half_self.z * axis.dot(axes_a[2]).abs();

            let projection_other = half_other.x * axis.dot(axes_b[0]).abs()
                + half_other.y * axis.dot(axes_b[1]).abs()
                + half_other.z * axis.dot(axes_b[2]).abs();

            if axis.dot(d).abs() > projection_self + projection_other {
                return false; // Separating axis found
            }
        }

        // Cross products axes
        for &a in &axes_a {
            for &b in &axes_b {
                let axis = a.cross(b);
                if axis.length_squared() < 1e-8 {
                    continue;
                } // skip near-zero vectors

                let projection_self = half_self.x * axis.dot(axes_a[0]).abs()
                    + half_self.y * axis.dot(axes_a[1]).abs()
                    + half_self.z * axis.dot(axes_a[2]).abs();

                let projection_other = half_other.x * axis.dot(axes_b[0]).abs()
                    + half_other.y * axis.dot(axes_b[1]).abs()
                    + half_other.z * axis.dot(axes_b[2]).abs();

                if axis.dot(d).abs() > projection_self + projection_other {
                    return false; // Separating axis found
                }
            }
        }
        true
    }
}

/// Equivalent of Unity's Physics.CheckBox
pub fn check_box(box_: &BoxCollider, colliders: &[BoxCollider]) -> bool {
    colliders.iter().any(|c| box_.overlaps(c))
}

/// Equivalent of Unity's Physics.OverlapBox
pub fn overlap_box<'a>(box_: &BoxCollider, colliders: &'a [BoxCollider]) -> Vec<&'a BoxCollider> {
    colliders
        .iter()
        .filter(|c| box_.overlaps(c))
        .collect()
}

/// Equivalent of Unity’s Physics.ComputePenetration
///
/// Returns `Some((direction, distance))` if overlapping.
/// Direction points from `a` toward `b`.
pub fn compute_penetration(a: &BoxCollider, b: &BoxCollider) -> Option<(Vec3, f32)> {
    let half_a = a.size * 0.5;
    let half_b = b.size * 0.5;

    let axes_a = a.axes();
    let axes_b = b.axes();

    let delta = b.position - a.position;

    // Generate 15 potential separating axes
    let mut axes = Vec::with_capacity(15);
    axes.extend_from_slice(&axes_a);
    axes.extend_from_slice(&axes_b);
    for &a_axis in &axes_a {
        for &b_axis in &axes_b {
            let cross = a_axis.cross(b_axis);
            if cross.length_squared() > 1e-8 {
                axes.push(cross.normalize());
            }
        }
    }

    let mut min_overlap = f32::INFINITY;
    let mut best_axis = Vec3::ZERO;

    for axis in axes {
        let axis = axis.normalize();

        // Project both boxes onto this axis
        let proj_a = half_a.x * axis.dot(axes_a[0]).abs()
            + half_a.y * axis.dot(axes_a[1]).abs()
            + half_a.z * axis.dot(axes_a[2]).abs();

        let proj_b = half_b.x * axis.dot(axes_b[0]).abs()
            + half_b.y * axis.dot(axes_b[1]).abs()
            + half_b.z * axis.dot(axes_b[2]).abs();

        // Distance between box centers along this axis
        let center_dist = axis.dot(delta).abs();

        let overlap = proj_a + proj_b - center_dist;
        if overlap < 0.0 {
            return None; // Separating axis found — no penetration
        }

        // Track smallest overlap
        if overlap < min_overlap {
            min_overlap = overlap;
            // Determine direction (from A to B)
            best_axis = if axis.dot(delta) < 0.0 { -axis } else { axis };
        }
    }

    Some((-best_axis, min_overlap))
}