using UnityEngine;

public static class Extensions
{
    // ---------- Vector3 Extensions ----------
    public static float[] ToArray(this Vector3 v)
    {
        return new float[] { v.x, v.y, v.z };
    }

    public static Vector3 ToVector3(this float[] arr)
    {
        if (arr == null || arr.Length != 3)
            throw new System.ArgumentException("Array must have exactly 3 elements.");
        return new Vector3(arr[0], arr[1], arr[2]);
    }

    // ---------- Quaternion Extensions ----------
    public static float[] ToArray(this Quaternion q)
    {
        return new float[] { q.x, q.y, q.z, q.w };
    }

    public static Quaternion ToQuaternion(this float[] arr)
    {
        if (arr == null || arr.Length != 4)
            throw new System.ArgumentException("Array must have exactly 4 elements.");
        return new Quaternion(arr[0], arr[1], arr[2], arr[3]);
    }
}
