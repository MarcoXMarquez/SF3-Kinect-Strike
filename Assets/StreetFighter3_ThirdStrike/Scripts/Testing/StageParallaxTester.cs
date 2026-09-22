using UnityEngine;

public class StageParallaxTester : MonoBehaviour
{
    [SerializeField] private float moveSpeed = 2f;
    [SerializeField] private float minX = -2.5f;
    [SerializeField] private float maxX = 2.5f;

    private float initialX;

    private void Awake()
    {
        initialX = transform.position.x;
    }

    private void Update()
    {
        float direction = 0f;

        if (Input.GetKey(KeyCode.LeftArrow)) direction -= 1f;
        if (Input.GetKey(KeyCode.RightArrow)) direction += 1f;

        if (Mathf.Approximately(direction, 0f)) return;

        Vector3 position = transform.position;
        position.x = Mathf.Clamp(
            position.x + direction * moveSpeed * Time.deltaTime,
            initialX + minX,
            initialX + maxX);
        transform.position = position;
    }
}
