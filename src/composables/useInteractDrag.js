import interact from 'interactjs'
import { onMounted, onUnmounted, ref, watch } from 'vue'

export function useInteractDrag(elementRef, options = {}) {
    const {
        onDragStart,
        onDragMove,
        onDragEnd,
        enabled = true,
        restrictToParent = false,
        snapToGrid = false,
        gridSize = 20,
        inertia = true
    } = options

    const isDragging = ref(false)
    const position = ref({ x: 0, y: 0 })
    let interactable = null

    const initInteract = () => {
        if (!elementRef.value || !enabled) return

        interactable = interact(elementRef.value)

        interactable.draggable({
            enabled: true,
            inertia,
            modifiers: [
                ...(restrictToParent ? [
                    interact.modifiers.restrictRect({
                        restriction: 'parent',
                        endOnly: true
                    })
                ] : []),
                ...(snapToGrid ? [
                    interact.modifiers.snap({
                        targets: [
                            interact.createSnapGrid({
                                x: gridSize,
                                y: gridSize,
                                offset: { x: 0, y: 0 }
                            })
                        ],
                        relativePoints: [{ x: 0, y: 0 }],
                        range: Infinity
                    })
                ] : [])
            ],
            listeners: {
                start(event) {
                    isDragging.value = true
                    onDragStart?.(event, { ...position.value })
                },
                move(event) {
                    position.value.x += event.dx
                    position.value.y += event.dy
                    event.target.style.transform = `translate(${position.value.x}px, ${position.value.y}px)`
                    onDragMove?.(event, { ...position.value })
                },
                end(event) {
                    isDragging.value = false
                    onDragEnd?.(event, { ...position.value })
                }
            }
        })

        interactable.styleCursor(false)
    }

    const destroy = () => {
        if (interactable) {
            interactable.unset()
            interactable = null
        }
    }

    const updatePosition = (x, y) => {
        position.value = { x, y }
        if (elementRef.value) {
            elementRef.value.style.transform = `translate(${x}px, ${y}px)`
        }
    }

    const enable = () => {
        if (interactable) {
            interactable.draggable({ enabled: true })
        }
    }

    const disable = () => {
        if (interactable) {
            interactable.draggable({ enabled: false })
        }
    }

    onMounted(() => {
        initInteract()
    })

    watch(enabled, (newValue) => {
        if (newValue) enable()
        else disable()
    })

    onUnmounted(() => {
        destroy()
    })

    return {
        isDragging,
        position,
        enable,
        disable,
        updatePosition,
        destroy
    }
}